import re
import os
from collections import defaultdict

from reviewme.ailinter.helpers import load_config
config = load_config()
MAX_RESULTS_PER_CATEGORY_TYPE = config["MAX_RESULTS_PER_CATEGORY_TYPE"]

# Constants
LIST_OF_ERROR_CATEGORIES = {
    "💡": "Logic Issues",
    "🏁": "Data Race Issues",
    "🔒": "Security Issues",
    "🚀": "Performance Issues",
    "☑️": "Consistency Issues",
    "🧪": "Testability Issues",
    "🧩": "Modularity Issues",
    "🌀": "Complexity Issues",
    "⚙️": "Optimization Issues",
    "⚠️": "Error Handling Issues",
}

DESCRIPTIONS_OF_ERROR_CATEGORIES = {
    "💡": "Logic Issues - Look for errors in the program's logic, such as incorrect calculations, incorrect control flow, or incorrect data manipulations.",
    "🔒": "Security Issues - Look for vulnerabilities that could be exploited by attackers, such as SQL injection, cross-site scripting (XSS), or insecure data transmission.",
    "🚀": "Performance Issues - Look for code that could be optimized for better performance, such as inefficient algorithms, unnecessary computations, or excessive memory usage.",
    "🏁": "Data Race Issues - Look for potential data races in multithreaded code, where two threads access shared data simultaneously and at least one of them modifies it",
    "☑️": "Consistency Issues - Look for inconsistencies in the codebase, such as different coding styles, inconsistent naming conventions, or inconsistent use of data structures.",
    "🧪": "Testability Issues - Look for code that is hard to test, such as tightly coupled components, lack of interfaces, or hidden dependencies.",
    "🧩": "Modularity Issues - Look for lack of modularity in the code, such as large modules, lack of encapsulation, or high coupling between modules.",
    "🌀": "Complexity Issues - Look for overly complex code, such as nested loops, deep recursion, or complex conditionals.",
    "⚙️": "Optimization Issues - Look for code that could be optimized for better readability, simplicity, or efficiency.",
    "⚠️": "Error Handling Issues - Look for improper error handling, such as ignoring exceptions, lack of error logging, or inappropriate error messages.",
}

PRIORITY_MAP = {
    "🔴": "🔴 High",
    "🟠": "🟠 Medium",
    "🟡": "🟡 Low"
}

# Functions
def extract_feedback_items(feedback_string):
    segments = feedback_string.split("**")[1:]
    feedback_items = []
    pattern = r"(.*?):(.*?):(\d+) (.*?)\s+\[(.*?)\] Fail: (.*?)\s+Fix: (.*?)(?=\*\*|$)"
    
    for i in range(0, len(segments), 2):
        if i+1 < len(segments):
            combined_item = segments[i] + segments[i+1]
            match = re.match(pattern, combined_item.strip(), re.MULTILINE | re.DOTALL)
            if match:
                feedback_items.append(match.groups())
            
    return feedback_items

# Function to organize feedback items
def organize_feedback_items(feedback_list):
    organized_feedback = []
    
    for feedback_string in feedback_list:
        items = extract_feedback_items(feedback_string)
        
        for item in items:
            filepath, function_name, line_number, category, priority, fail, fix = item
            
            # Convert category to emoji-based key
            category_key = None
            for key, value in LIST_OF_ERROR_CATEGORIES.items():
                # if value.split()[0] in category.upper():
                if value.split()[0] in category:
                    category_key = key
                    break
            
            if not category_key:
                continue
            
            # Create a dictionary for each feedback item
            feedback_item = {
                "filepath": filepath,
                "function_name": function_name,
                "line_number": line_number,
                "error_category": category_key,
                "priority_score": priority,
                "fail": fail,
                "fix": fix
            }
            
            organized_feedback.append(feedback_item)

    return organized_feedback

# Function to format feedback for print
def format_feedback_for_print(organized_feedback, max_items_per_category=MAX_RESULTS_PER_CATEGORY_TYPE):
    if not organized_feedback:
        return "No feedback items to display."
    # Format the organized feedback
    result = ""
    
    # Group feedback items by category and priority
    feedback_by_category = defaultdict(lambda: defaultdict(list))
    for feedback_item in organized_feedback:
        feedback_by_category[feedback_item["error_category"]][feedback_item["priority_score"]].append(feedback_item)
    
    for cat_emoji, cat_name in LIST_OF_ERROR_CATEGORIES.items():
        if cat_emoji not in feedback_by_category:
            continue
        
        category_feedback = feedback_by_category[cat_emoji]
        
        result += f"\n======== {cat_emoji} {cat_name} ========\n\n"
        
        for priority_emoji, priority_fullname in PRIORITY_MAP.items():
            if priority_fullname not in category_feedback:
                continue
            
            result += f"--{PRIORITY_MAP[priority_emoji]}--\n\n"
            
            for item in category_feedback[priority_fullname][:max_items_per_category]:
                filepath, function_name, line_number, fail, fix = item["filepath"], item["function_name"], item["line_number"], item["fail"], item["fix"]
                result += f"* {filepath}:{line_number} {function_name}\n- Fail: {fail}\n- Fix: {fix}\n\n"
    
    return result

def get_files_to_review(organized_feedback):
    files_to_review_set = set()  # Using a set to avoid duplicates
    
    for feedback_item in organized_feedback:
        filepath = feedback_item["filepath"]
        files_to_review_set.add(filepath)
                
    return list(files_to_review_set)


# 2. Creating the okay_file_list
def get_okay_files(directory_path, files_to_review_list):
    excluded_dirs = ["bin", "lib", "include", "env"]
    okay_file_list = []
    
    # Use os.walk to get all files in the directory
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            full_filepath = os.path.join(dirpath, filename)
            if full_filepath not in files_to_review_list and full_filepath.endswith(".py"):
                if not any([excluded_dir in full_filepath for excluded_dir in excluded_dirs]):
                    okay_file_list.append(full_filepath)
                
    return okay_file_list
