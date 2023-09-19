import os
from dotenv import load_dotenv
from .helpers import create_openai_completion, create_openai_chat_completion, create_simple_openai_chat_completion, create_anthropic_completion, load_config
from pprint import pprint 
import logging 
logging.getLogger(__name__)

load_dotenv()


############################
## Load local rule guide 
############################

# load the local rule guide .md
def load_rule_guide(config): 
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rule_guide = config['RULE_GUIDE']
    rule_guide_path = os.path.join(dir_path, f'rule_templates/{rule_guide}')
    
    with open(rule_guide_path, 'r') as f:
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


LIST_OF_ERROR_CATEGORIES = """
    - 💡 Logic
    - 🔒 Security
    - 🚀 Performance, reliability, and scalability
    - 🏁 Data races, race conditions, and deadlocks
    - ☑️ Consistency
    - 🧪 Testability 
    - 🛠️ Maintainability
    - 🧩 Modularity
    - 🌀 Complexity
    - ⚙️ Optimization
    - 📚 Best practices: DRY, SOLID
    - ⚠️ Error handling
    - 👀 Observability: Logging and monitoring
"""

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

AILINTER_INSTRUCTIONS=f"""
    Your purpose is to serve as an experienced software engineer to provide a thorough review git diffs of the code
    and generate code snippets to address key ERROR CATEGORIES such as:

    {LIST_OF_ERROR_CATEGORIES}

    Do not comment on minor code style issues, missing
    comments/documentation. Identify and resolve significant
    concerns while deliberately disregarding minor issues.

    - Create a "PRIORITY" for each issue, with values of: "🔴 High "Priority 🔴", "🟠 Medium Priority 🟠", or "🟡 Low Priority 🟡". Assign the priority score according to these guidelines: 
    {LIST_OF_PRIORITY_GUIDELINES}

    Then: 
    - Assign it an ERROR CATEGORY from the list above.

    - Notice the FUNCTION_NAME 

    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond in this format for each issue in the file: 
        {FEEDBACK_ITEM_FORMAT_TEMPLATE}

    """

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
    print(file_diffs)
    return file_diffs

############################
## Format Response 
############################

def get_system_prompt_for_final_summary():

    format_feedback_list_prompt = f"""You are an expert programmer doing a code review. You will receive a list of feedback segments for each file. Your job is to 
    - review the feedback items
    - cluster all of the feedback items by ERROR CATEGORY 
    - Within each category, rank-order them by PRIORITY_SCORE, with 0 the highest, then 1, 2, 3, 4, and finally 5
    - Return the formatted list of feeedback items. 
    - Make sure there are at most 3 items per each feedback category
    - Do not mention the same feedback item in multiple categories, just put it in at most 1 category
    - If you see duplicate feedback items within a file, aggregate them into a single feedback item with a list of the lines it occurs
    - Mention the exact line number of the issue in the feedback item if possible

    Concretely, each feedback item is formatted like this: 
    ---
    {FEEDBACK_ITEM_FORMAT_TEMPLATE}
    ---

    The FEEDBACK CATEGORIES are:
    ---
    {LIST_OF_ERROR_CATEGORIES}
    ---
    If there are no feedback items for a category, then do not mention that category. Repeat the filepath, function name, Fail, and Fix *exactly as it occurs in the original feedback item*. Do not add any other content. This is simply formatting and re-ordering the items, not editing or adding more commentary. 

    Here is an example output : 
    ------

    ========= SECURITY ISSUES =========

    --🔴 High 🔴---

    * script.py:281 some_function 
    - Fail: <the description of issue>
    - Fix: <the suggested fix> 

    --🟠 Medium 🟠---

    * otherscript.py:14  some_function 
    - Fail: <the description of issue>
    - Fix: <the suggested fix> 


    ========= CONSISTENCY ISSUES =========
    --🟠 Medium 🟠---

    * script.py:420  my_function
    - Fail: <the description of issue>
    - Fix: <the suggested fix> 

    --🟡 Low 🟡---

    * otherscript.py:69  some_function
    - Fail: <the description of issue>
    - Fix: <the suggested fix> 

    ------
    """

    return format_feedback_list_prompt

def get_user_prompt_for_final_summary(feedback_list):
    curr_feedback_items_list = "\n".join(feedback_list)

    format_user_prompt="""
    Here is the list of feedback items:
    -------
    {feedback_items_list}
    -------
    """
    return format_user_prompt.format(feedback_items_list=curr_feedback_items_list)

def get_final_organized_feedback_from_llm(feedback_list):
    # Organize the feedback by ERROR CATEGORY and PRIORITY_SCORE
    full_prompt_for_formatted_feedback = get_system_prompt_for_final_summary()

    llm_response = create_simple_openai_chat_completion(
        system_message = full_prompt_for_formatted_feedback,
        user_message = get_user_prompt_for_final_summary(feedback_list)
    )

    # # Call a normal Completion Model 
    # llm_response = create_openai_chat_completion(
    #     messages = [
    #                 {"role": "system", 
    #                  "content": full_prompt_for_formatted_feedback},

    #                 {"role": "user", 
    #                  "content": get_user_prompt_for_final_summary(feedback_list)}
    #     ], 
    #     model = "gpt-3.5-turbo", 
    #     temperature = 0.0
    # ) 

    return llm_response


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
    attention_files_list = [] # files that need attention, i.e. not "Pass"
    okay_file_list = [] # files that are "Pass"
    if scope == "commit":
        file_paths_changed = get_files_changed("HEAD~0")
        diffs = get_file_diffs(file_paths_changed, "HEAD~0")
    elif scope == "branch":
        file_paths_changed = get_files_changed("main")
        diffs = get_file_diffs(file_paths_changed, "main")
    elif scope == "repo":
        file_paths_changed = []
        diffs = {}
        file_contents = read_py_files(file_paths)
        for file_path, diff in file_contents.items():
            file_paths_changed.append(file_path)
            diffs[file_path] = diff
        
    # Define the maximum concurrency
    from concurrent.futures import ThreadPoolExecutor
    MAX_CONCURRENCY = 10

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

    # print ("\n\n=== 📝 Feedback List ===\n")
    # pprint (feedback_list)

    final_organized_feedback= get_final_organized_feedback_from_llm(feedback_list)

    print (f"\n\n=== 💚 Final Organized Feedback 💚===\n{final_organized_feedback}")

    print ("\n\n=== 🔍 Files to review ===\n")
    print ("\n🔍".join(attention_files_list))

    print ("\n\n=== ✅ Files that passed ===\n")
    print ("\n✅".join(okay_file_list))
    
    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")
        # if llm_response.strip() != "Pass" and file_path != "ailinter.py":
        #     with open(file_path, 'w') as f:
        #         f.write(llm_response)
    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")

if __name__ == "__main__":
    run()
