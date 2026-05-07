# function to retreave the readme and the swagger APIs
import re
import requests
import json 

from src.data_model import API

def _to_raw_github_url(url: str) -> str:
    """
    Convert a GitHub web page URL to the equivalent raw content URL.

    Example:
      https://github.com/owner/repo/tree/branch/path/to/dir#readme
      → https://raw.githubusercontent.com/owner/repo/branch/path/to/dir/README.md

      https://github.com/owner/repo/blob/branch/path/to/file.md
      → https://raw.githubusercontent.com/owner/repo/branch/path/to/file.md
    """
    # Match GitHub web URLs: /tree/... or /blob/...
    match = re.match(
        r"https://github\.com/([^/]+/[^/]+)/(tree|blob)/([^#?]+)",
        url
    )
    if not match:
        return url  # not a GitHub web URL, return unchanged

    repo_path = match.group(1)   # e.g. "owner/repo"
    ref_type  = match.group(2)   # "tree" or "blob"
    rest      = match.group(3)   # e.g. "master/path/to/dir" or "master/path/to/file.md"

    if ref_type == "tree":
        # Directory page with #readme anchor → append README.md
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/{rest}/README.md"
    else:
        # File page (blob) → direct raw content
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/{rest}"

    return raw_url


def get_markdown(link: str):
    raw_url = _to_raw_github_url(link)
    res = requests.get(url=raw_url)
    return res.text


def get_api_list_from_swagger(link):
    api_list = get_markdown(link)

    json_api_list = json.loads(api_list)["paths"]
    api_paths = json_api_list.keys()

    preprocessed_api_list = []

    for api in api_paths:
        path = json_api_list[api]
        for method in path.keys():
            preprocessed_api_list.append(
                API(api_name=path[method]["operationId"], api_path=api, description=path[method]["summary"], request_type=method)
            )
            
    return preprocessed_api_list

def api_list_to_string(api_list):
    apis = ""
    for api in api_list:
        apis += api.api_name + ", "
    # Remove the trailing comma and add a newline
    apis = apis.rstrip(", ") + "\n"
    return apis
