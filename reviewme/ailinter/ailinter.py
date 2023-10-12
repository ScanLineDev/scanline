import json
import logging
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from attrs import asdict
from dotenv import load_dotenv
from parea.utils.trace_utils import trace

from reviewme.ailinter.format_results import (
    organize_feedback_items,
    format_feedback_for_print,
    PRIORITY_MAP,
    DESCRIPTIONS_OF_ERROR_CATEGORIES,
    LIST_OF_ERROR_CATEGORIES,
)
from reviewme.ailinter.helpers import (
    create_openai_chat_completion,
    load_config,
    MODEL_OPTIONS,
)

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
    ".gvy",
]


############################
## Load local rule guide
############################
def get_install_dir():
    dir_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return dir_path


def load_rule_guide(config):
    dir_path = get_install_dir()
    rule_guide = config["RULE_GUIDE"]

    if getattr(sys, "_MEIPASS", False):
        rule_guide_path = os.path.join(
            dir_path, f"reviewme/ailinter/rule_templates/{rule_guide}"
        )
    else:
        rule_guide_path = os.path.join(dir_path, f"rule_templates/{rule_guide}")

    with open(rule_guide_path, "r") as f:
        return f.read()


############################
## Set up based on config
############################
config = load_config()
RULE_GUIDE_MD = load_rule_guide(config)


############################
## Load all code in the directory
############################
def read_py_files(file_paths):
    file_contents = {}

    for file_path in file_paths:
        logging.debug(f"Reading extension{os.path.splitext(file_path)[1]}")
        if os.path.splitext(file_path)[1] not in SUPPORTED_FILE_EXTENSIONS:
            logging.debug(
                f"Skipping {file_path} because it is not a supported file extension"
            )
            continue

        try:
            with open(file_path, "r") as f:
                file_contents[file_path] = f.read()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            continue

    return file_contents


# Check for local imports in the code and append the imported code
def check_and_append_local_imports(code, file_paths):
    lines = code.split("\n")
    for line in lines:
        if line.startswith("import ") or line.startswith("from "):
            try:
                module_name = line.split(" ")[1].split(".")[0]
                if module_name + ".py" in file_paths:
                    imported_code = read_py_files([module_name + ".py"])[
                        module_name + ".py"
                    ]
                    code += "\n" + imported_code
            except Exception as e:
                print(f"An error occurred while processing import statements: {e}")
    return code


############################
## LLM call and Prompt
############################

LIST_OF_PRIORITY_GUIDELINES = """🔴 High: 
    This priority is assigned to code issues that have a critical impact on the program's functionality, performance, 
    or security. These issues can cause system crashes, data loss, or security breaches, 
    and should be addressed immediately to prevent severe consequences.

    🟠 Medium: 
    This priority is given to code issues that may not immediately affect the program's functionality but could 
    potentially lead to bigger problems in the future or make the code harder to maintain.
    Performance issues that degrade user experience but don't cripple the system.

    🟡 Low:
    This priority is assigned to minor issues that don't significantly affect the program's functionality or 
    performance, such as style inconsistencies or lack of comments, and can be addressed at a later time.
"""

FEEDBACK_ITEM_FORMAT_TEMPLATE = """
    ** <FILEPATH>:<FUNCTION_NAME>:<LINE_NUMBER> <ERROR CATEGORY> ** 
    [<PRIORITY_SCORE>] Fail: <a short one-sentence description of the issue >
    Fix: <a short one-sentence suggested fix >
    """

# format the imported dict to use inside another f-string
DESCRIPTIONS_OF_ERROR_CATEGORIES_STRING = "\n" + "\n".join(
    [f"- {emoji} {name}" for emoji, name in DESCRIPTIONS_OF_ERROR_CATEGORIES.items()]
)

AILINTER_INSTRUCTIONS = f"""
    Your purpose is to serve as an experienced developer and to provide a thorough review of git diffs of the code
    and generate code snippets to address key ERROR CATEGORIES such as:
    {DESCRIPTIONS_OF_ERROR_CATEGORIES_STRING}

    You'll be given the git diffs, and next the full content of the original file before the edits.

    Please read through the code line by line to deeply understand it, take your tie, and look carefully for what 
    can be improved
    
    Identify and resolve significant concerns 
    Make sure before claiming an issue that you've also looked at the full content of the original file so you 
    have full context

    Make sure to review the code in the context of the programming language standards and best practices.
    
    - Create a "PRIORITY" for each issue, with values of one of the following: {list(PRIORITY_MAP.values())}. 
    Assign the priority score according to these guidelines: 

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


@trace
def get_chat_completion_messages_for_review(code, full_file_content):
    if full_file_content is not None:
        chat_messages = [
            {
                "role": "system",
                "content": f"""{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n === FULL FILE 
                CONTENT BEFORE CHANGES FOR REFERENCE=== \n{full_file_content} \n""",
            },
            {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code}\n```"},
        ]
    else:
        chat_messages = [
            {
                "role": "system",
                "content": f"{AILINTER_INSTRUCTIONS} \n\n === RULE GUIDE: === \n{RULE_GUIDE_MD} \n\n \n",
            },
            {"role": "user", "content": f"=== CODE TO REVIEW === ```\n{code}\n```"},
        ]
    return chat_messages


############################
## LLM call and Prompt
############################


def get_final_organized_feedback(feedback_list):
    organized_feedback_items = organize_feedback_items(feedback_list)
    formatted_feedback = format_feedback_for_print(organized_feedback_items)

    return formatted_feedback


############################
## Main
############################
@trace(
    tags=["reviewme", "ailinter"],
    end_user_identifier="user_joel",
)
def review_code(code, full_file_content, model):
    delay = 0.1
    success = False
    numAttempts = 1
    attemptsLeft = numAttempts
    while not success and attemptsLeft > 0:
        llm_response = create_openai_chat_completion(
            messages=get_chat_completion_messages_for_review(code, full_file_content),
            model=model,
        )
        print(f"LLM Response: {json.dumps(asdict(llm_response), indent=2)}")

        if llm_response.status == "success":
            return llm_response.content

        time.sleep(delay)
        delay *= random.uniform(1.5, 3)
        attemptsLeft -= 1

    # hail mary try gpt3.5 with 16k context window see if this works!
    llm_response = create_openai_chat_completion(
        messages=get_chat_completion_messages_for_review(code, full_file_content),
        model="gpt-3.5-turbo-16k",
    )
    return llm_response.content


def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


def get_current_branch():
    # use git cli to figure out which branch we're on
    result = subprocess.run(
        "git branch --show-current",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.stdout:
        return result.stdout.strip()
    else:
        return None


def select_candidate_files(file_paths, k=3):
    # get all files starting at the git root of this project
    file_paths = (
        subprocess.check_output(["git", "ls-files"]).decode("utf-8").split("\n")
    )

    # filter for programming source code files
    file_paths = [
        f
        for f in file_paths
        if f.endswith(
            (
                ".js",
                ".py",
                ".java",
                ".cpp",
                ".h",
                ".c",
                ".html",
                ".css",
                ".xml",
                ".json",
                ".yml",
                ".yaml",
                ".sh",
                ".md",
                ".txt",
                ".go",
                ".ts",
            )
        )
    ]

    # filter for files with at least 500 and less than 5000 characters
    file_char_counts = {
        f: os.stat(f).st_size
        for f in file_paths
        if os.stat(f).st_size >= 500 and os.stat(f).st_size < 5000
    }

    # randomize order o the file_char_counts dictionary keys so its different on every call to select_candidate_files
    import random

    keys = list(file_char_counts.keys())
    random.shuffle(keys)
    file_char_counts = {k: file_char_counts[k] for k in keys}

    # sample up to k files such that the sum of all the characters is less than 5000
    total_chars = 0
    candidate_files = []
    for f, char_count in file_char_counts.items():
        if total_chars + char_count < 5000:
            candidate_files.append(f)
            total_chars += char_count
            if len(candidate_files) == k:
                break

    return candidate_files


@trace(metadata={"base": "run"})
def run(model: str) -> str:
    file_paths = [
        "../LocalTest/game_logger.py",
        "../LocalTest/initial_cards.py",
        "../LocalTest/test.py",
        "../LocalTest/data.py",
    ]

    feedback_list = []

    file_paths_changed = []
    # not actually getting diffs, just reading whole file to review and using "diffs" for
    # naming consistency with the other scope options above
    diffs = {}
    file_contents = read_py_files(file_paths)
    for file_path, diff in file_contents.items():
        file_paths_changed.append(file_path)
        diffs[file_path] = diff

    # Define the maximum concurrency

    MAX_CONCURRENCY = 4

    # Create a ThreadPoolExecutor with the maximum concurrency
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        # Submit the file review completion jobs to the executor
        futures = []
        for file_path in file_paths_changed:
            try:
                content = diffs[file_path]
                print(f"\n== Checking {file_path} ==")

                if not content:
                    print(f"Skipping {file_path} because it is empty")
                    continue

                # Append imported local modules' code to the existing code
                current_code_to_review = check_and_append_local_imports(
                    content, file_paths
                )
                full_file_content = read_file(file_path)

                time.sleep(0.25)
                futures.append(
                    executor.submit(
                        review_code, current_code_to_review, full_file_content, model
                    )
                )
            except Exception as e:
                logging.error(
                    f"Error while reviewing {file_path}: {e}, skipping this file"
                )

        print(
            "\nProcessing and generating feedback for all files. This will take several minutes...\n"
        )

        # Wait for all the jobs to complete
        for future in futures:
            llm_response = future.result()

            if not llm_response:
                continue

            feedback_list.append(llm_response)

    ########################################################
    ## Format and Display the Results
    ########################################################

    if not feedback_list:
        print("\n\n=== No feedback found. All done. ===\n")
        return ""

    # get the organized *dictionary* of feedback items
    organized_feedback_dict = organize_feedback_items(feedback_list)

    # get the *pretty print* for them for terminal
    final_organized_issues_to_print = format_feedback_for_print(organized_feedback_dict)

    print(f"\n\n=== 💚 Final Organized Feedback 💚===\n{final_organized_issues_to_print}")

    print(
        "\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n"
    )

    ############################
    ## Format the dict to save to CSV and JS
    ############################
    # Check if the feedback dictionary is empty
    if not organized_feedback_dict:
        print("No feedback found. All done.")
        return ""

    # Add the emoji and error category name for each error category
    for feedback in organized_feedback_dict:
        feedback[
            "error_category"
        ] = f"{feedback['error_category']} {LIST_OF_ERROR_CATEGORIES[feedback['error_category']]}"

    # Re-order the columns
    organized_feedback_dict = [
        {
            k: v
            for k, v in sorted(
                feedback.items(),
                key=lambda item: [
                    "error_category",
                    "priority_score",
                    "filepath",
                    "function_name",
                    "line_number",
                    "fail",
                    "fix",
                ].index(item[0]),
            )
        }
        for feedback in organized_feedback_dict
    ]

    # Rename the columns
    for feedback in organized_feedback_dict:
        feedback["Error Category"] = feedback.pop("error_category")
        feedback["Priority"] = feedback.pop("priority_score")
        feedback["Filepath"] = feedback.pop("filepath")
        feedback["Function Name"] = feedback.pop("function_name")
        feedback["Line Number"] = feedback.pop("line_number")
        feedback["Issue"] = feedback.pop("fail")
        feedback["Suggested Fix"] = feedback.pop("fix")

    # Re-order the rows by priority. first high, then medium, then low
    priority_order = ["🔴 High", "🟠 Medium", "🟡 Low"]
    organized_feedback_dict.sort(key=lambda x: priority_order.index(x["Priority"]))

    # Remove the word "Issues" from the "Error Category" column
    for feedback in organized_feedback_dict:
        feedback["Error Category"] = feedback["Error Category"].replace(" Issues", "")

    return json.dumps(organized_feedback_dict, indent=4)


if __name__ == "__main__":
    json_data = run(model=random.choice(MODEL_OPTIONS))
    print(f"json_data: {json_data}")
    print("Done.")
