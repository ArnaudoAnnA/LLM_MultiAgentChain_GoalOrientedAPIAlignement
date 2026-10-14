
"""
llm_client.py

This module provides utility functions to interact with different LLM APIs,
such as Google's Gemini (generator) and Groq's Qwen (critic, via the OpenAI-compatible
API). It includes functions to generate responses using various models, handling
system prompts and formatting.

API clients are initialized lazily, one per API key, to support key rotation under
rate limits.

The critic function is still named `generate_response_llama` although its model is
Qwen, not LLaMA: renaming it would touch every call site for no functional gain.

Both providers' keys come from `data_key.api_keys` (loaded from `.env`).
"""
from openai import OpenAI, RateLimitError
from google import genai
from google.genai import errors, types

from data_key.api_keys import get_key_gemini, count_gemini_keys, get_key_groq, count_groq_keys

# --- Generator (Gemini) ---
GENERATOR_MODEL = "gemini-2.5-flash"
GENERATOR_TEMPERATURE = 0
GENERATOR_SEED = 42  # best-effort: reproducibility is a provider declaration, not a guarantee
GENERATOR_MAX_OUTPUT_TOKENS = 32000  # 12000 still truncated the low-level goal list of systems with 30+ high-level goals
# The critic is a reasoning model: its thinking tokens count against this limit, and the prompt
# alone can exceed 11k tokens when a long goal list is evaluated.
CRITIC_MAX_OUTPUT_TOKENS = 16000
GENERATOR_THINKING_BUDGET = 0  # off: the generator runs as a non-reasoning model
_GENERATOR_MAX_KEY_ROTATIONS = 2  # per key, mirrors generate_response_llama's count_Llama_keys()*2

# One genai.Client per API key, created on first use and reused across calls.
_gemini_clients: dict[str, genai.Client] = {}


def _get_gemini_client(api_key: str) -> genai.Client:
    client = _gemini_clients.get(api_key)
    if client is None:
        client = genai.Client(api_key=api_key)
        _gemini_clients[api_key] = client
    return client


def generate_response(prompt, sys_prompt, response_format=None) -> str:
    config_kwargs = dict(
        system_instruction=sys_prompt,
        temperature=GENERATOR_TEMPERATURE,
        seed=GENERATOR_SEED,
        max_output_tokens=GENERATOR_MAX_OUTPUT_TOKENS,
        thinking_config=types.ThinkingConfig(thinking_budget=GENERATOR_THINKING_BUDGET),
    )
    if response_format is not None:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_format
    config = types.GenerateContentConfig(**config_kwargs)

    api_key = get_key_gemini()
    max_attempts = count_gemini_keys() * _GENERATOR_MAX_KEY_ROTATIONS
    last_exception: Exception | None = None

    for _ in range(max_attempts):
        client = _get_gemini_client(api_key)
        try:
            response = client.models.generate_content(
                model=GENERATOR_MODEL,
                contents=prompt,
                config=config,
            )
        except errors.ClientError as e:
            last_exception = e
            if e.code in (429, 403, 402):  # rate limit / quota / prepaid credits exhausted -> rotate key
                api_key = get_key_gemini(increment_counter=True)
                continue
            raise  # e.g. 400: an invalid response_schema must surface immediately, not be masked
        except errors.ServerError as e:
            last_exception = e
            if e.code == 503:  # model overloaded, retry the same key
                continue
            raise

        if response_format is not None:
            if response.parsed is None:
                candidate = response.candidates[0] if response.candidates else None
                finish_reason = candidate.finish_reason if candidate else None
                raise ValueError(
                    "Gemini returned no parsed structured output "
                    f"(finish_reason={finish_reason}, prompt_feedback={response.prompt_feedback})"
                )
            return response.parsed
        else:
            if not response.text:
                candidate = response.candidates[0] if response.candidates else None
                finish_reason = candidate.finish_reason if candidate else None
                raise ValueError(
                    "Gemini returned an empty response "
                    f"(finish_reason={finish_reason}, prompt_feedback={response.prompt_feedback})"
                )
            return response.text

    raise last_exception


# --- Critic (Qwen on Groq, via the OpenAI-compatible endpoint) ---
llama = OpenAI(
    api_key=get_key_groq(),
    base_url="https://api.groq.com/openai/v1"
)


def generate_response_llama(prompt, sys_prompt):
    global llama
    last_exception = None

    for _ in range(0, count_groq_keys()*2):
        try:
            response = llama.beta.chat.completions.parse(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                model = "qwen/qwen3.8-27b",
                max_tokens = CRITIC_MAX_OUTPUT_TOKENS,
                temperature = 0
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            last_exception = e

            llama = OpenAI(
                api_key=get_key_groq(increment_counter=True),
                base_url="https://api.groq.com/openai/v1"
            )

    raise last_exception
