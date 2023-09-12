import os
import yaml
from dotenv import load_dotenv
from pprint import pprint 

import openai
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

################################
## Misc Helpers  
################################

# load the local config.yaml 
def load_config():
    with open('ailinter/config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

################################
## LLMs
################################
# Load .env file
load_dotenv()
ANTRHOPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
openai.api_key = os.getenv("OPENAI_API_KEY")

#######
## OpenAI: ChatCompletion
#######

def create_openai_chat_completion (messages, 
                                   model = "gpt-4",
                                   temperature = config['DEFAULT_TEMPERATURE']): 
  
  try: 
    completion = openai.ChatCompletion.create(
    model=model, 
    messages = messages,
    temperature=temperature,
    )
    return completion.choices[0].message.content
  except Exception as e:
      print(f"An error occurred: {e}")
  

#######
## OpenAI: Completion
#######

def create_openai_completion (prompt, 
                              model = "text-davinci-003", 
                              temperature = config['DEFAULT_TEMPERATURE']): 
  
  try: 
    completion_object = openai.Completion.create(
    model=model, 
    prompt=prompt, 
    temperature=config['DEFAULT_TEMPERATURE'],
    )
    return completion_object.choices[0].text
  except Exception as e:
    print(f"An error occurred: {e}")
  

################################
## Anthropic : Completion 
################################

def create_anthropic_completion(prompt):
  anthropic = Anthropic(
      # defaults to os.environ.get("ANTHROPIC_API_KEY")
      api_key=ANTRHOPIC_API_KEY,
  )
  try: 
    completion = anthropic.completions.create(
    model="claude-2",
    prompt=f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}",
  )
    return completion.completion
  except Exception as e:
    print(f"An error occurred: {e}")
  

################################
## LLM MAP 
################################

MODEL_MAP = {
   "text-davinci-003": create_openai_completion,
   "gpt-4-turbo": create_openai_completion, 
   "claude-2": create_anthropic_completion
}
