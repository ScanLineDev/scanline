import os
from dotenv import load_dotenv
from .helpers import create_openai_completion, create_openai_chat_completion, create_anthropic_completion, load_config
from pprint import pprint 
load_dotenv()

############################
## Load local rule guide 
############################

# load the local rule guide .md
def load_rule_guide(config): 
    rule_guide = config['RULE_GUIDE']
    with open(f"ailinter/rule_templates/{rule_guide}", 'r') as f:
        return f.read()

config = load_config()
RULE_GUIDE_MD = load_rule_guide(config)

############################
## Load all code in the directory 
############################

# Read Python files and return content
def read_py_files(file_paths):
    file_contents = {}
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_contents[file_path] = f.read()
    return file_contents

# Check for local imports in the code and append the imported code
def check_and_append_local_imports(code, file_paths):
    lines = code.split('\n')
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            try:
                module_name = line.split(' ')[1].split('.')[0]
                if module_name + '.py' in file_paths:
                    imported_code = read_py_files([module_name + '.py'])[module_name + '.py']
                    code += '\n' + imported_code
            except Exception as e:
                print(f"An error occurred while processing import statements: {e}")

    return code

############################
## LLM call and Prompt 
############################

AILINTER_INSTRUCTIONS="""
    You are an expert python programmer and debugger. 
    Please read the following code file. 


    (1) Please say if you anticipate any issues when running it. 
    Look for subtle issues that may not be obvious at first glance.
    Look for internal consistency, and for external consistency with the rest of the codebase.
    Be alert! Look for any subtle human errors where the code doesn't do what the function or documentation hopes for it to do.

    (2) In addition, see the style guide below. Ensure that the code adheres to the style guide. 
    
    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond in this format for each issue in the file: 
        Fail: {a short one-sentence description of the issue }
        Fix: {a short one-sentence suggested fix }

    """

#########
## Construct the prompt 
#########

def get_completion_prompt (code):
    completion_prompt = f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === {RULE_GUIDE_MD} \n\n === CODE TO REVIEW === ```\n {code} \n```"
    return completion_prompt

def get_chat_completion_messages(code):
    chat_messsages = [
                    {"role": "system", "content": f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n"},
                    {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code} \n```"}
                ]
    return chat_messsages

############################
## LLM call and Prompt 
############################

def run(): 
    # Get all .py files in this directory and subdirectories
    file_paths = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_file_path = os.path.join(root, file)
                file_paths.append(full_file_path)

    # Read the content of each Python file
    file_contents = read_py_files(file_paths)
    
    for file_path, content in file_contents.items():
        print(f"\n== Checking {file_path} ==")

        if content == "" or content == None:
            continue

        # Append imported local modules' code to the existing code
        current_code_to_review = check_and_append_local_imports(content, file_paths)
        
        ### TESTING 
        pprint (get_chat_completion_messages(current_code_to_review))
               ###
        
        # Call openai Chat Completion Model 
        llm_response = create_openai_chat_completion(
            messages = get_chat_completion_messages(current_code_to_review)
        ) 

        

        ### Call a normal Completion Model 
        # llm_response = create_anthropic_completion(
        #     prompt = get_completion_prompt(current_code_to_review)
        # ) 
        
        print(f"Code Review: \n{llm_response}")
        
        ### --- Future feature --- 
        ## If the OpenAI response is not "Pass", rewrite the .py file with the OpenAI response
        # if llm_response.strip() != "Pass" and file_path != "ailinter.py":
        #     with open(file_path, 'w') as f:
        #         f.write(llm_response)
    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")

if __name__ == "__main__":
    run()