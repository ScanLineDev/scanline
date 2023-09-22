import re
import os
from collections import defaultdict

from reviewme.ailinter.helpers import load_config
config = load_config()
MAX_RESULTS_PER_CATEGORY_TYPE = config["MAX_RESULTS_PER_CATEGORY_TYPE"]

# Constants
FEEDBACK_CATEGORIES = {
    "💡": "LOGIC ISSUES",
    "🔒": "SECURITY ISSUES",
    "🚀": "PERFORMANCE ISSUES",
    "🏁": "DATA RACE ISSUES",
    "☑️": "CONSISTENCY ISSUES",
    "🧪": "TESTABILITY ISSUES",
    "🛠️": "MAINTAINABILITY ISSUES",
    "🧩": "MODULARITY ISSUES",
    "🌀": "COMPLEXITY ISSUES",
    "⚙️": "OPTIMIZATION ISSUES",
    "📚": "BEST PRACTICES ISSUES",
    "⚠️": "ERROR HANDLING ISSUES",  # Adjusted this line
    "👀": "OBSERVABILITY ISSUES"
}

PRIORITY_MAP = {
    "🔴": "🔴 High Priority 🔴",
    "🟠": "🟠 Medium Priority 🟠",
    "🟡": "🟡 Low Priority 🟡"
}

# Functions
def extract_feedback_items(feedback_string):
    segments = feedback_string.split("**")[1:]
    feedback_items = []
    pattern = r"(.*?):(.*?):(\d+) (.*?)\s+\[(.*?)\] Fail: (.*?)\s+Fix: (.*?)(?=\*\*|$)"
    
    for i in range(0, len(segments), 2):
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
            for key, value in FEEDBACK_CATEGORIES.items():
                if value.split()[0] in category.upper():
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
    # Format the organized feedback
    result = ""
    
    # Group feedback items by category and priority
    feedback_by_category = defaultdict(lambda: defaultdict(list))
    for feedback_item in organized_feedback:
        feedback_by_category[feedback_item["error_category"]][feedback_item["priority_score"]].append(feedback_item)
    
    for cat_emoji, cat_name in FEEDBACK_CATEGORIES.items():
        if cat_emoji not in feedback_by_category:
            continue
        
        category_feedback = feedback_by_category[cat_emoji]
        
        result += f"\n======== {cat_name} ========\n\n"
        
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
    okay_file_list = []
    
    # Use os.walk to get all files in the directory
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            full_filepath = os.path.join(dirpath, filename)
            if full_filepath not in files_to_review_list and full_filepath.endswith(".py"):
                okay_file_list.append(full_filepath)
                
    return okay_file_list
