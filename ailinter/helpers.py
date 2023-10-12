import os

import yaml
from dotenv import load_dotenv
from parea import Parea
from parea.schemas.models import (
    Completion,
    LLMInputs,
    ModelParams,
    Message,
    CompletionResponse,
)
from parea.utils.trace_utils import trace


################################
## Misc Helpers
################################


# load the local config.yaml
def load_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


config = load_config()

################################
## LLMs
################################
# Load .env file
load_dotenv()


#######
## Parea: ChatCompletion
#######
p = Parea(api_key=os.getenv("PAREA_API_KEY"))

MODEL_OPTIONS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-32k",
    "claude-instant-1",
    "claude-2",
    "meta-llama/Llama-2-70b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "meta-llama/Llama-2-7b-chat-hf",
    "codellama/CodeLlama-34b-Instruct-hf",
]


@trace
def create_openai_chat_completion(messages, model, temperature=0) -> CompletionResponse:
    try:
        return p.completion(
            data=Completion(
                llm_configuration=LLMInputs(
                    model=model,
                    model_params=ModelParams(
                        temp=temperature,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                    ),
                    messages=[Message(**d) for d in messages],
                )
            )
        )
    except Exception as e:
        print(f"An error occurred: {e}")
