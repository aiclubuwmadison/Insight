from dotenv import dotenv_values
from json import load
from copy import deepcopy

env_config = dotenv_values(".env")

try:
    with open(env_config["PROMPT_JSON"],'r') as prompt_file:
        prompt = load(prompt_file)
        content = prompt["CONTENT"]
        content_args = prompt["CONTENT_ARGS"]
        configs = prompt["CONFIGS"]
except Exception as e:
    raise RuntimeError(f"ERROR: Encountered {e} while loading prompt parameters")

class Prompt:
    def __init__(self, request):
        global content
        global content_args
        global configs

        prompt_content = deepcopy(content)
        
        for arg in content_args:
            if not request.get(arg, None):
                raise RuntimeError(f"ERROR: client request did not specify parameter \"{arg}\"")
            prompt_content[arg] = request[arg]

        self.content = prompt_content
        self.configs = configs