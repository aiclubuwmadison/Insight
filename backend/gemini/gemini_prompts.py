from dotenv import dotenv_values
from json import load
from copy import deepcopy

env_config = dotenv_values(".env")

with open(env_config["PROMPT_JSON"],'r') as prompt_file:
    prompt_template = load(prompt_file)


class Prompt:
    def __init__(self,request):
        global prompt_template

        self.contents = deepcopy(prompt_template["contents"])
        self.contents = self.contents.format(language=request["language"],code=request["code"])
        self.config = deepcopy(prompt_template["config"])
        

       