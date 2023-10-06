import os
import yaml
from dotenv import load_dotenv
from pprint import pprint 
import openai

################################
## Misc Helpers  
################################

# load the local config.yaml 
def load_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

################################
## LLMs
################################
# Load .env file
load_dotenv()
# ANTRHOPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
openai.api_key = os.getenv("OPENAI_API_KEY")

#######
## OpenAI: ChatCompletion
#######

def create_openai_chat_completion (messages, 
                                   model = "gpt-3.5-turbo-16k",
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
  
def create_simple_openai_chat_completion(
      system_message, user_message):
  return create_openai_chat_completion(
      messages=[
          {"role": "system",
              "content": system_message,},
          {"role": "user","content": user_message,},
      ],
  )


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

# def create_anthropic_completion(prompt):
#   anthropic = Anthropic(
#       # defaults to os.environ.get("ANTHROPIC_API_KEY")
#       api_key=ANTRHOPIC_API_KEY,
#   )
#   try: 
#     completion = anthropic.completions.create(
#     model="claude-2",
#     prompt=f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}",
#   )
#     return completion.completion
#   except Exception as e:
#     print(f"An error occurred: {e}")
  

################################
## LLM MAP 
################################

MODEL_MAP = {
   "text-davinci-003": create_openai_completion,
   "gpt-4-turbo": create_openai_completion, 
  #  "claude-2": create_anthropic_completion
}

