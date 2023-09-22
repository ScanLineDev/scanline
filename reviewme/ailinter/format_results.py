import re
from collections import defaultdict

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
    print ('running organize_feedback_items')
    """
    The decision to use a list within a list (or a "double list") for the line numbers was to accommodate feedback items that may have multiple occurrences within the same file.

    In other words, if the same feedback item appears on multiple lines within the same file and function, instead of listing it multiple times, the feedback can be aggregated into a single item with a list of line numbers. This design choice simplifies the display and avoids redundant feedback.

    For example, if the same issue was found on lines 5, 7, and 9 in somefile.py within the function some_function, the feedback could be represented as:
    """
    organized_feedback = defaultdict(lambda: defaultdict(list))
    
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
            
            # Check for duplicates and aggregate lines
            duplicate_found = False
            for existing_item in organized_feedback[category_key][priority]:
                if existing_item[0] == filepath and existing_item[1] == function_name and existing_item[3] == fail:
                    existing_item[2].append(line_number)
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                organized_feedback[category_key][priority].append([filepath, function_name, [line_number], fail, fix])

    from pprint import pprint 
    pprint (dict(organized_feedback))
    return dict(organized_feedback)

# Function to format feedback for print
def format_feedback_for_print(organized_feedback, max_items_per_category=3):
    print ('running format_feedback_for_print')
    # Format the organized feedback
    result = ""
    
    for cat_emoji, cat_name in FEEDBACK_CATEGORIES.items():
        if cat_emoji not in organized_feedback:
            continue
        
        category_feedback = organized_feedback[cat_emoji]
        
        # if not category_feedback:
        #     continue
        
        result += f"======== {cat_name} ========\n\n"
        
        for priority_emoji, priority_fullname in PRIORITY_MAP.items():  # Using the keys from PRIORITY_MAP directly
            if priority_fullname not in category_feedback:
                continue
            
            result += f"--{PRIORITY_MAP[priority_emoji]}--\n\n"
            
            for item in category_feedback[priority_fullname][:max_items_per_category]:
                filepath, function_name, lines, fail, fix = item
                lines_str = ",".join(lines)
                result += f"* {filepath}:{lines_str} {function_name}\n- Fail: {fail}\n- Fix: {fix}\n\n"
    
    return result
