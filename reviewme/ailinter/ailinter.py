import os, sys
from dotenv import load_dotenv
from pprint import pprint 
import logging 

from reviewme.ailinter.helpers import create_openai_chat_completion, create_simple_openai_chat_completion, load_config
from reviewme.ailinter.format_results import organize_feedback_items, format_feedback_for_print, get_files_to_review, get_okay_files, PRIORITY_MAP, LIST_OF_ERROR_CATEGORIES, DESCRIPTIONS_OF_ERROR_CATEGORIES

###########
logging.getLogger(__name__)
load_dotenv()

############################
## Load local rule guide 
############################

# load the local rule guide .md

def load_rule_guide(config):
    dir_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    rule_guide = config['RULE_GUIDE']
    
    if getattr(sys, '_MEIPASS', False):
        rule_guide_path = os.path.join(dir_path, f'reviewme/ailinter/rule_templates/{rule_guide}')
    else:
        rule_guide_path = os.path.join(dir_path, f'rule_templates/{rule_guide}')

    with open(rule_guide_path, 'r') as f:
        return f.read()

config = load_config()
RULE_GUIDE_MD = load_rule_guide(config)

SUPPORTED_FILETYPES = config['SUPPORTED_FILETYPES']
print (f"Supported filetypes: {SUPPORTED_FILETYPES}")

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

LIST_OF_PRIORITY_GUIDELINES = """High Priority:
Issues that pose immediate security risks, cause data loss, or critically break functionality.
Problems that have a direct and substantial impact on business revenue.
Must-have features or issues that are absolutely essential for a release.

Medium Priority:
Performance issues that degrade user experience but don't cripple the system.
Important but non-critical features, and moderate user-experience concerns.
Issues impacting internal tools and operations but not directly affecting customers.

Low Priority:
Nice-to-have features and minor UI/UX issues that don't affect core functionality.
Tech debt items that are important long-term but not urgent.
Issues identified as non-essential for the current release cycle or having low overall impact.
"""

FEEDBACK_ITEM_FORMAT_TEMPLATE = """
    ** <FILEPATH>:<FUNCTION_NAME>:<LINE_NUMBER> <ERROR CATEGORY> ** 
    [<PRIORITY_SCORE>] Fail: <a short one-sentence description of the issue >
    Fix: <a short one-sentence suggested fix >
    """
# format the imported dict to use inside of another f-string 
DESCRIPTIONS_OF_ERROR_CATEGORIES_STRING = ("\n" + "\n".join([f"- {emoji} {name}" for emoji, name in DESCRIPTIONS_OF_ERROR_CATEGORIES.items()]))

AILINTER_INSTRUCTIONS=f"""
    Your purpose is to serve as an experienced developer and to provide a thorough review of git diffs of the code
    and generate code snippets to address key ERROR CATEGORIES such as:
    {DESCRIPTIONS_OF_ERROR_CATEGORIES_STRING}

    Do not comment on minor code style issues, missing
    comments/documentation. Identify and resolve significant
    concerns while deliberately disregarding minor issues.

    Make sure to review the code in the context of the programming language standards and best practices.
    
    - Create a "PRIORITY" for each issue, with values of one of the following: {list(PRIORITY_MAP.values())}. Assign the priority score according to these guidelines: 
    
    {LIST_OF_PRIORITY_GUIDELINES}

    - Mention the exact line number of the issue in the feedback item if possible

    Then: 
    - Assign it an ERROR CATEGORY from the list above.

    - Notice the FUNCTION_NAME 

    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond in this format for each issue in the file: 
        {FEEDBACK_ITEM_FORMAT_TEMPLATE}

    """

print ("---- AILINTER INSTRUCTIONS: ----  ", AILINTER_INSTRUCTIONS)
#########
## Construct the prompt 
#########

def get_completion_prompt (code):
    completion_prompt = f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === {RULE_GUIDE_MD} \n\n === CODE TO REVIEW === ```\n {code} \n```"
    return completion_prompt

def get_chat_completion_messages_for_review(code):
    chat_messsages = [
                    {"role": "system", "content": f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n"},
                    {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code} \n```"}
                ]
    return chat_messsages

############################
## LLM call and Prompt 
############################

def get_files_changed(target):
    # Get list of all files that changed on this git branch compared to main
    file_paths_changed = os.popen("git diff --name-only {0}".format(target)).read().split("\n")

    # add . prefix to all files
    result = []
    for file_path in file_paths_changed:
        if file_path != "":
            result.append("./" + file_path)

    return result

def get_file_diffs(file_paths, target):

    file_diffs = {}
    for file_path in file_paths:
            file_diffs[file_path] = os.popen("git diff --unified=0 {0} {1}".format(target, file_path)).read()
            print("git diff --unified=0 {0} {1}".format(target, file_path))
    # print(file_diffs)
    return file_diffs


def get_final_organized_feedback(feedback_list):

    organized_feedback_items = organize_feedback_items(feedback_list)
    formatted_feedback = format_feedback_for_print(organized_feedback_items)

    return formatted_feedback

############################
## Main 
############################

def review_code(code):
    llm_response = create_openai_chat_completion(
        messages = get_chat_completion_messages_for_review(code), 
        model = "gpt-4",
    ) 

    return llm_response

def run(scope, onlyReviewThisFile): 
    # Get all .py files in this directory and subdirectories
    excluded_dirs = ["bin", "lib", "include", "env"]
    file_paths = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_file_path = os.path.join(root, file)
                file_paths.append(full_file_path)


    # Get all .py files in this directory and subdirectories that changed on this git branch compared to master
    # file_paths_changed = get_files_changed()
    # diffs = get_file_diffs(file_paths_changed)

    feedback_list = [] 

    if scope == "commit":
        file_paths_changed = get_files_changed("HEAD~0")
        diffs = get_file_diffs(file_paths_changed, "HEAD~0")
    elif scope == "branch":
        try:
            file_paths_changed = get_files_changed("master")
            diffs = get_file_diffs(file_paths_changed, "master")
        except Exception as e:
            pass
        try:
            file_paths_changed = get_files_changed("main")
            diffs = get_file_diffs(file_paths_changed, "main")
        except Exception as e:
            pass
    elif scope == "repo":
        file_paths_changed = []
        diffs = {}
        file_contents = read_py_files(file_paths)
        for file_path, diff in file_contents.items():
            file_paths_changed.append(file_path)
            diffs[file_path] = diff
        
    # Define the maximum concurrency
    from concurrent.futures import ThreadPoolExecutor
    MAX_CONCURRENCY = 1

    # Create a ThreadPoolExecutor with the maximum concurrency
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        # Submit the file review completion jobs to the executor
        futures = []
        for file_path in file_paths_changed:
            if onlyReviewThisFile != "" and onlyReviewThisFile not in file_path:
                continue

                # check that onlyThisFile is in the file path or else skip 
            if onlyReviewThisFile != "" and onlyReviewThisFile not in file_path:
                logging.debug(f"Skipping {file_path} because it does not match onlyReviewThisFile {onlyReviewThisFile}")
                continue

            content = diffs[file_path]
            print(f"\n== Checking {file_path} ==")

            if content == "" or content == None:
                continue

            # Append imported local modules' code to the existing code
            current_code_to_review = check_and_append_local_imports(content, file_paths)
            
            import time
            time.sleep(0.25)
            futures.append(executor.submit(review_code, current_code_to_review))

        # Wait for all the jobs to complete
        for future in futures:
            llm_response = future.result()

            if llm_response is None:
                continue

            feedback_list.append(llm_response)

    # # for testing 
    # print ("\n\n=== 📝 Feedback List ===\n")
    # pprint (feedback_list)

    # get the organized *dictionary* of feedback items
    organized_feedback_dict = organize_feedback_items(feedback_list)

    # get the *pretty print* for them for terminal 
    final_organized_issues_to_print = format_feedback_for_print(organized_feedback_dict)

    # get the list of files *to review*
    files_to_review_list = get_files_to_review(organized_feedback_dict)
    okay_file_list = get_okay_files(directory_path=".", files_to_review_list=files_to_review_list)

    print (f"\n\n=== 💚 Final Organized Feedback 💚===\n{final_organized_issues_to_print}")

    print ("\n\n=== 🔍 Files to review ===")
    print ("\n🔍 " + "\n🔍 ".join(files_to_review_list))

    ## Add logic to get the files that were examined: either file_contents or file_paths_changed, depending on 'scope' 
    print ("\n\n=== ✅ Files that passed ===")
    print ("\n✅ " + "\n✅ ".join(okay_file_list))
    
    # print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")
        # if llm_response.strip() != "Pass" and file_path != "ailinter.py":
        #     with open(file_path, 'w') as f:
        #         f.write(llm_response)
    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")

if __name__ == "__main__":
    run("commit", "")
