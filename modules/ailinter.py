import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
load_dotenv()

AILINTER_INSTRUCTIONS="""
    You are an expert python programmer and debugger. 
    Please read the following code file. 
    Please say if you anticipate any issues when running it. 
    Look for subtle issues that may not be obvious at first glance.
    Look for internal consistency, and for external consistency with the rest of the codebase.
    Be alert! Look for any subtle human errors where the code doesn't do what the function or documentation hopes for it to do.
    Imagine running through every function in the code, look for 
    
    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond in this format for each issue in the file: 
        Fail: {a short one-sentence description of the issue }
        Fix: {a short one-sentence suggested fix }
    """


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

# LLM call to check if the code will run or has issues
def call_openai_api(code):
    payload = {
        "prompt": AILINTER_INSTRUCTIONS + "\n\n\n ```" + code + "\n```",
    }
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": AILINTER_INSTRUCTIONS},
                {"role": "user", "content": f"{code}"}
            ], 
            temperature = 0.1,
        )

        # response = openai.Completion.create(
        #     engine="text-davinci-003",
        #     prompt=payload['prompt'],
        #     max_tokens = 1000,
        #     temperature = 0.1,
        # )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"


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
        new_content = check_and_append_local_imports(content, file_paths)
        
        # print ("new content:", new_content)
        # Make an API call to OpenAI to check if the code will run
        openai_response = call_openai_api(new_content)
        
        print(f"Code Review: \n{openai_response}")
        
        # # If the OpenAI response is not "Pass", rewrite the .py file with the OpenAI response
        # if openai_response.strip() != "Pass" and file_path != "ailinter.py":
        #     with open(file_path, 'w') as f:
        #         f.write(openai_response)
    print ("\n\n=== Done. ===\nSee above for code review. \nNow running the rest of your code...\n")


if __name__ == "__main__":
    run()