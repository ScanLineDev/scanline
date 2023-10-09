from datetime import datetime
import subprocess
import os, sys
from dotenv import load_dotenv
from pprint import pprint 
import logging 
import argparse
import shutil
import json

#to run local webapp
import http.server
import socketserver
import socketserver

from reviewme.ailinter.helpers import create_openai_chat_completion, create_simple_openai_chat_completion, load_config
from reviewme.ailinter.format_results import organize_feedback_items, format_feedback_for_print, get_files_to_review, get_okay_files, PRIORITY_MAP, LIST_OF_ERROR_CATEGORIES, DESCRIPTIONS_OF_ERROR_CATEGORIES

###########
logging.getLogger(__name__)
load_dotenv()

SUPPORTED_FILE_EXTENSIONS = [
    ".js",
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".cc",
    ".cxx",
    ".c++",
    ".cs",
    ".php",
    ".ts",
    ".sh",
    ".bash",
    ".swift",
    ".kt",
    ".kts",
    ".rb",
    ".go",
    ".rs",
    ".m",
    ".mm",
    ".r",
    ".scala",
    ".pl",
    ".pm",
    ".lua",
    ".groovy",
    ".grvy",
    ".gy",
    ".gvy"
]

############################
## Load local rule guide 
############################
def get_install_dir():
    dir_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return dir_path

def load_rule_guide(config):
    dir_path = get_install_dir()
    rule_guide = config['RULE_GUIDE']
    
    if getattr(sys, '_MEIPASS', False):
        rule_guide_path = os.path.join(dir_path, f'reviewme/ailinter/rule_templates/{rule_guide}')
    else:
        rule_guide_path = os.path.join(dir_path, f'rule_templates/{rule_guide}')

    with open(rule_guide_path, 'r') as f:
        return f.read()

############################
## Set up based on config 
############################
config = load_config()
RULE_GUIDE_MD = load_rule_guide(config)

SAVED_REVIEWS_DIR=config['SAVED_REVIEWS_DIR']

# Create the folder, in the local directory, if it doesn't exist already
os.makedirs(SAVED_REVIEWS_DIR, exist_ok=True)

############################
## Load all code in the directory 
############################
def read_py_files(file_paths):
    file_contents = {}

    for file_path in file_paths:
        logging.debug(f"Reading extension{os.path.splitext(file_path)[1]}")
        if os.path.splitext(file_path)[1] not in SUPPORTED_FILE_EXTENSIONS:
            logging.debug(f"Skipping {file_path} because it is not a supported file extension")
            continue
            
        try:
            with open(file_path, 'r') as f:
                file_contents[file_path] = f.read()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            continue

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

LIST_OF_PRIORITY_GUIDELINES = """🔴 High: 
    This priority is assigned to code issues that have a critical impact on the program's functionality, performance, or security. These issues can cause system crashes, data loss, or security breaches, and should be addressed immediately to prevent severe consequences.

    🟠 Medium: 
    This priority is given to code issues that may not immediately affect the program's functionality but could potentially lead to bigger problems in the future or make the code harder to maintain.
    Performance issues that degrade user experience but don't cripple the system.

    🟡 Low:
    This priority is assigned to minor issues that don't significantly affect the program's functionality or performance, such as style inconsistencies or lack of comments, and can be addressed at a later time.
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

    You'll be given the git diffs, and next the full content of the original file before the edits.

    Please read through the code line by line to deeply understand it, take your tie, and look carefully for what can be improved
    Identify and resolve significant concerns 
    Make sure before claiming an issue that you've also looked at the full content of the original file so you have full context

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

############################
## Construct the prompt 
############################

def get_completion_prompt (code):
    completion_prompt = f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === {RULE_GUIDE_MD} \n\n === CODE TO REVIEW === ```\n {code} \n```"
    return completion_prompt

def get_chat_completion_messages_for_review(code, full_file_content):
    if full_file_content is not None:
        chat_messsages = [
                    {"role": "system", "content": f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n === FULL FILE CONTENT BEFORE CHANGES FOR REFERENCE=== \n{full_file_content} \n"},
                    {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code}\n```"},
                ]
    else:
        chat_messsages = [
                        {"role": "system", "content": f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n \n"},
                        {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code}\n```"},
                    ]
    return chat_messsages

############################
## LLM call and Prompt 
############################

def get_main_branch_name():
    # Get the name of the main branch (either main or master)
    result = subprocess.run(
        "git ls-remote --heads origin | grep 'refs/heads/main'",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.stdout:
        return "main"
    else:
        return "master"

def get_files_changed(target):
    EXCLUDED_EXTENSIONS = ['.snap', ".pyc"]
    # Get list of all files that changed on this git branch compared to main
    file_paths_changed = os.popen("git diff --name-only {0}".format(target)).read().split("\n")
    # add . prefix to all files
    result = []
    for file_path in file_paths_changed:
        file_extension = os.path.splitext(file_path)[1]
        if file_path != "" and file_extension in SUPPORTED_FILE_EXTENSIONS:
            result.append("./" + file_path)

    return result

def get_file_diffs(file_paths, target):
    # Get the diff for each file compared to target
    # Note: Won't include any files that only exist upstream but not locally. 

    file_diffs = {}
    for file_path in file_paths:
        logging.debug(f"Getting diff for {file_path} and target {target}")
        file_diffs[file_path] = os.popen("git diff --unified=0 {0} {1} 2>/dev/null".format(target, file_path)).read()
    return file_diffs

def get_final_organized_feedback(feedback_list):

    organized_feedback_items = organize_feedback_items(feedback_list)
    formatted_feedback = format_feedback_for_print(organized_feedback_items)

    return formatted_feedback

############################
## Main 
############################

def review_code(code, full_file_content, model):
    import time
    import random

    delay = 0.1
    success = False
    numAttempts = 10
    attemptsLeft = numAttempts
    while not success and attemptsLeft > 0:
        llm_response = create_openai_chat_completion(
            messages = get_chat_completion_messages_for_review(code, full_file_content),
            model = model,
        ) 

        if llm_response is not None and "Rate limit reached" not in llm_response:
            return llm_response

        print(f"llm_response: {llm_response}")
        time.sleep(delay)
        delay *= random.uniform(1.5, 3)
        attemptsLeft -= 1

    # hail mary try gpt3.5 with 16k context window see if this works!
    llm_response = create_openai_chat_completion(
        messages = get_chat_completion_messages_for_review(code, full_file_content),
        model = "gpt-3.5-turbo-16k",
    )
    return llm_response

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def run(scope, onlyReviewThisFile, model): 

    # Get all .py files in this directory and subdirectories
    excluded_dirs = ["bin", "lib", "include", "env", "node_modules"]
    file_paths = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            full_file_path = os.path.join(root, file)
            file_paths.append(full_file_path)

    feedback_list = [] 

    if scope == "commit":
        file_paths_changed = get_files_changed("HEAD~0")
        diffs = get_file_diffs(file_paths_changed, "HEAD~0")
    elif scope == "branch":
        main_branch_name = get_main_branch_name()
        remote_branch_name = f"origin/{main_branch_name}"
        try:
            file_paths_changed = get_files_changed(remote_branch_name)
            diffs = get_file_diffs(file_paths_changed, remote_branch_name)
        except Exception as e:
            pass
        try:
            file_paths_changed = get_files_changed(remote_branch_name)
            diffs = get_file_diffs(file_paths_changed, remote_branch_name)
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

    # preliminary scan all files see how big this change is
    total_chars = 0
    file_size_dict = {}
    ESTIMATED_AVG_CHARS_PER_TOKEN = 4
    for file_path in list(file_paths_changed):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                total_chars += len(content)
                file_size_dict[file_path] = len(content) / ESTIMATED_AVG_CHARS_PER_TOKEN
        except Exception as e:
            file_paths_changed.remove(file_path)
            logging.debug(f"Error while reading {file_path}: {e}")
            
    GPT4_PRICING_1K_TOKENS = 0.03
    numTokens = total_chars/ESTIMATED_AVG_CHARS_PER_TOKEN

    # TODO on 1ST INSTALL ask for preference -> save initial config file 
    # config file stores all global configs like folders/files to ignore, persistent settings default loaded by scanline
    # dynamic options mid run: Y = continue, 2 = ignore files beyond X size 3 bail out/don't run. 4. select files you want
    if numTokens > 30000: 
        FILE_TOKENS_LIMIT = 10000
        print("Heads up this change is roughly {0} tokens which is fairly large. On GPT4 as of October 2023 this may cost >${1} USD?".format(numTokens, (numTokens/1000) * GPT4_PRICING_1K_TOKENS))
        selection = input("Choose one of the following options and press enter:\n\t(1) continue review\n\t(2) exit review\n\t(3) ignore files larger than 10k tokens")
        while selection != "1" and selection != "2" and selection != "3":
            selection = input("Ehem... please select a valid option 1, 2, 3...")
        if selection == "2":
            print("Probably for the best 👍")
            return
        if selection == "3":
            print("Ignoring files larger than 10k tokens")
            for file_path in list(file_paths_changed):
                if file_size_dict.get(file_path, 0) > FILE_TOKENS_LIMIT:
                    print(f"Ignoring {file_path} because it is {file_size_dict[file_path]} >= {FILE_TOKENS_LIMIT} tokens")
                    file_paths_changed.remove(file_path)
                    numTokens = numTokens - file_size_dict[file_path]

    if numTokens > 30000: 
        FILE_TOKENS_LIMIT = 10000
        print("Heads up this change is still roughly {0} tokens which is fairly large. On GPT4 as of October 2023 this may cost >${1} USD?".format(numTokens, (numTokens/1000) * GPT4_PRICING_1K_TOKENS))
        selection = input("Options enter one of the following and press enter:\n\t(1) continue review\n\t(2) exit review")
        while selection != "1" and selection != "2":
            selection = input("Ehem... please select a valid option 1, 2")
        if selection == "2":
            print("Probably for the best 👍")
            return
 
    # Create a ThreadPoolExecutor with the maximum concurrency
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        # Submit the file review completion jobs to the executor
        futures = []
        for file_path in file_paths_changed:
            try:
                if onlyReviewThisFile != "" and onlyReviewThisFile not in file_path:
                    continue

                    # check that onlyThisFile is in the file path or else skip 
                if onlyReviewThisFile != "" and onlyReviewThisFile not in file_path:
                    logging.debug(f"Skipping {file_path} because it does not match onlyReviewThisFile {onlyReviewThisFile}")
                    continue

                content = diffs[file_path]
                print(f"\n== Checking {file_path} ==")

                if content == "" or content == None:
                    print(f"Skipping {file_path} because it is empty")
                    continue

                # Append imported local modules' code to the existing code
                current_code_to_review = check_and_append_local_imports(content, file_paths)
                full_file_content = None # read_file(file_path)
                
                import time
                time.sleep(0.25)
                futures.append(executor.submit(review_code, current_code_to_review, full_file_content, model))
            except Exception as e:
                logging.error(f"Error while reviewing {file_path}: {e}, skipping this file")


        # Estimate number of minutes to run the scan. This varies based on the speed of the user's machine. w
        estimated_num_minutes = numTokens / 2500
        estimated_max_minutes = round(estimated_num_minutes * 1.4)
        estimated_min_minutes = round(estimated_num_minutes * 0.6)
        # print (f"\nProcessing and generating feedback for the files listed. This may take between {estimated_min_minutes} and {estimated_max_minutes} minutes...\n")
        print ("\nProcessing and generating feedback for all files. This will take several minutes...\n")

        # Wait for all the jobs to complete
        for future in futures:
            llm_response = future.result()

            if llm_response is None:
                continue

            feedback_list.append(llm_response)

    ########################################################
    ## Format and Display the Results
    ########################################################

    if feedback_list == [] or feedback_list == None:
        print ("\n\n=== No feedback found. All done. ===\n")
        return

    # get the organized *dictionary* of feedback items
    organized_feedback_dict = organize_feedback_items(feedback_list)

    # get the *pretty print* for them for terminal 
    final_organized_issues_to_print = format_feedback_for_print(organized_feedback_dict)

    # get the list of files *to review*
    files_to_review_list = get_files_to_review(organized_feedback_dict)
    okay_file_list = get_okay_files(directory_path=".", files_to_review_list=files_to_review_list)

    print (f"\n\n=== 💚 Final Organized Feedback 💚===\n{final_organized_issues_to_print}")

    #print ("\n\n=== 🔍 Files to review ===")
    #print ("\n🔍 " + "\n🔍 ".join(files_to_review_list))


    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")

    ############################
    ### Save this review for record-keeping and display
    ### Saves the organized feedback results into a local folder. This can be referenced and updated later, in terminal or the streamlit app 
    ############################
    # Format the dataframe 
    # now = datetime.now().strftime("%Y%m%d-%H%M%S")
    # SAVED_REVIEWS_DIR = "/var/tmp"

    # for the webapp MVP, we aren't passing the unique filename as a variable, so we just write to the same filename each time for now 

    ############################
    ## Format the dict to save to CSV and JS
    ############################
    # Check if the feedback dictionary is empty
    if not organized_feedback_dict:
        print("No feedback found. All done.")
        return

    # Add the emoji and error category name for each error category
    for feedback in organized_feedback_dict:
        feedback['error_category'] = f"{feedback['error_category']} {LIST_OF_ERROR_CATEGORIES[feedback['error_category']]}"

    # Re-order the columns
    organized_feedback_dict = [{k: v for k, v in sorted(feedback.items(), key=lambda item: ['error_category', 'priority_score', 'filepath', 'function_name', 'line_number', 'fail', 'fix'].index(item[0]))} for feedback in organized_feedback_dict]

    # Rename the columns
    for feedback in organized_feedback_dict:
        feedback['Error Category'] = feedback.pop('error_category')
        feedback['Priority'] = feedback.pop('priority_score')
        feedback['Filepath'] = feedback.pop('filepath')
        feedback['Function Name'] = feedback.pop('function_name')
        feedback['Line Number'] = feedback.pop('line_number')
        feedback['Issue'] = feedback.pop('fail')
        feedback['Suggested Fix'] = feedback.pop('fix')

    # Re-order the rows by priority. first high, then medium, then low
    priority_order = ["🔴 High", "🟠 Medium", "🟡 Low"]
    organized_feedback_dict.sort(key=lambda x: priority_order.index(x['Priority']))

    # Remove the word "Issues" from the "Error Category" column
    for feedback in organized_feedback_dict:
        feedback['Error Category'] = feedback['Error Category'].replace(' Issues', '')

    ############################
    ## Save to JS file for webapp html 
    json_data = json.dumps(organized_feedback_dict)
    js_data = f"var data = {json_data};"
    SAVED_REVIEWS_DIR = "/var/tmp/scanline"
    os.makedirs(SAVED_REVIEWS_DIR, exist_ok=True)
    absolute_js_file_path = os.path.join(SAVED_REVIEWS_DIR, f"data.js")
    with open(absolute_js_file_path, 'w') as f:
        f.write(js_data)

    print(f"\n\n=== ✅ Saved this review to {absolute_js_file_path} ===\n")
    print("✅ Code review complete.")

    ############################
    ### Copy the index.html, styles.css and scripts.js files to the /var/tmp directory
    ############################

    dir_path = get_install_dir()
    # copy index.html 
    src = os.path.join(dir_path, 'webapp-test/index.html')
    index_html_file = '/var/tmp/scanline/index.html'
    shutil.copy2(src, index_html_file)

    # copy scripts.js
    src = os.path.join(dir_path, 'webapp-test/scripts.js')
    dst = '/var/tmp/scanline/scripts.js'
    shutil.copy2(src, dst)

    # copy styles.css
    src = os.path.join(dir_path, 'webapp-test/styles.css')
    dst = '/var/tmp/scanline/styles.css'
    shutil.copy2(src, dst)

    ############################
    ## Open the .html 
    print (f"\n\n=== ✅ Opening the webapp in your browser... ===\n")
    print (f"index_html_file: {index_html_file}")

    import webbrowser
    webbrowser.open_new_tab(f"file://{index_html_file}")

