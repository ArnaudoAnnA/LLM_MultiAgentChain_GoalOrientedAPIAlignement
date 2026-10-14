"""
api_keys.py

Thread-safe round-robin over provider API keys declared in the process environment
(loaded from a local `.env` file, never hardcoded here or in git).

Both the generator (Gemini) and the critic (Groq) read their keys from here.

Env convention: `<PREFIX>_1`, `<PREFIX>_2`, ... (1-indexed, no gaps). The count of
available keys is derived from what is actually present, not declared separately —
an `int(os.getenv(...))` on a missing variable would fail with an opaque `TypeError`
instead of a clear "no keys configured" error.

Why `threading.Lock` and not `multiprocessing.Value` (as in the reference script
`APIKeysManager.py` this module's idea is adapted from): the notebook parallelizes
datasets with `Thread` + `Semaphore(MAX_PARALLEL_RUNS)`, not with separate processes.
A process-safe primitive would be the wrong tool here.
"""
import os
import threading

from dotenv import load_dotenv

load_dotenv()


class _KeyRotator:
    """Round-robin over `<env_prefix>_1`, `<env_prefix>_2`, ... read from the environment."""

    def __init__(self, env_prefix: str):
        self._env_prefix = env_prefix
        self._lock = threading.Lock()
        self._index = 0
        self._keys = self._load_keys()

    def _load_keys(self) -> list[str]:
        keys = []
        i = 1
        while True:
            value = os.getenv(f"{self._env_prefix}_{i}")
            if value is None:
                break
            keys.append(value)
            i += 1
        return keys

    def current_key(self) -> str:
        if not self._keys:
            raise RuntimeError(
                f"No API keys configured for '{self._env_prefix}'. "
                f"Set {self._env_prefix}_1 (and optionally _2, _3, ...) in .env."
            )
        with self._lock:
            return self._keys[self._index]

    def rotate(self) -> str:
        """Advance to the next key and return it. No-op (returns the only key) if there is one."""
        with self._lock:
            if not self._keys:
                raise RuntimeError(
                    f"No API keys configured for '{self._env_prefix}'. "
                    f"Set {self._env_prefix}_1 (and optionally _2, _3, ...) in .env."
                )
            self._index = (self._index + 1) % len(self._keys)
            return self._keys[self._index]

    def count(self) -> int:
        return len(self._keys)


# One rotator per provider. Add a new line here (plus two thin wrappers) for the
# next provider that needs rotation.
_gemini_keys = _KeyRotator("GOOGLE_API_KEY")
_groq_keys = _KeyRotator("GROQ_API_KEY")


def get_key_gemini(increment_counter: bool = False) -> str:
    """
    Return the Gemini API key (generator).
    Supports round-robin over multiple keys to handle Google rate limits.
    """
    if increment_counter:
        return _gemini_keys.rotate()
    return _gemini_keys.current_key()


def count_gemini_keys() -> int:
    """Return the number of available Gemini keys."""
    return _gemini_keys.count()


def get_key_groq(increment_counter: bool = False) -> str:
    """
    Return the Groq API key (critic, Qwen).
    Supports round-robin over multiple keys to handle Groq rate limits.
    """
    if increment_counter:
        return _groq_keys.rotate()
    return _groq_keys.current_key()


def count_groq_keys() -> int:
    """Return the number of available Groq keys."""
    return _groq_keys.count()
