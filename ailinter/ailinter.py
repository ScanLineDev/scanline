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
    Your purpose is to serve as an experienced
    software engineer to provide a thorough review git diffs of tecode
    and generate code snippets to address key areas such as:
    - Logic
    - Security
    - Performance
    - Data races
    - Consistency
    - Error handling
    - Maintainability
    - Modularity
    - Complexity
    - Optimization
    - Best practices: DRY, SOLID, KISS

    Do not comment on minor code style issues, missing
    comments/documentation. Identify and resolve significant
    concerns while deliberately disregarding minor issues.

    Create a "priority" score for each issue, from 0 - 5, where 0 is the highest priority and 5 is the lowest priority (i.e. not important).

    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond in this format for each issue in the file: 
        [{priority_score}] Fail: {a short one-sentence description of the issue }
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

def get_files_changed():
    # Get list of all files that changed on this git branch compared to main
    file_paths_changed = os.popen("git diff --name-only main").read().split("\n")

    # add . prefix to all files
    result = []
    for file_path in file_paths_changed:
        if file_path != "":
            result.append("./" + file_path)

    return result

def get_file_diffs(file_paths):
    file_diffs = {}
    for file_path in file_paths:
        file_diffs[file_path] = os.popen(f"git diff --unified=0 main {file_path}").read()
    return file_diffs

def run(): 
    excluded_dirs = ["bin", "lib", "include", "env"]
    file_paths = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_file_path = os.path.join(root, file)
                file_paths.append(full_file_path)


    # Get all .py files in this directory and subdirectories that changed on this git branch compared to master
    file_paths_changed = get_files_changed()
    diffs = get_file_diffs(file_paths_changed)
    
    for file_path in file_paths_changed:
        content = diffs[file_path]
        print(f"\n== Checking {file_path} ==")

        if content == "" or content == None:
            continue

        # Append imported local modules' code to the existing code
        current_code_to_review = check_and_append_local_imports(content, file_paths)
        
        ### TESTING 
        # pprint (get_chat_completion_messages(current_code_to_review))
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