import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
load_dotenv()

# Function to read Python files and return content
def read_py_files(file_paths):
    file_contents = {}
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_contents[file_path] = f.read()
    return file_contents


# Function to call OpenAI API to check if the code will run or has issues
def call_openai_api(code):
    instructions = """
    You are an expert python programmer and debugger. 
    Please read the following code file. 
    Please say if you anticipate any issues when running it. Look for subtle issues that may not be obvious at first glance. Look for internal consistency, and for external consistency with the rest of the codebase.
    
    - If it looks OK, respond with the word "Pass", and nothing else.
    - If not, then please respond with the word "Fail:", then a description of the issues, and options for solving it. 
    """
    payload = {
        "prompt": instructions + "\n\n\n ```" + code + "\n```",
    }
    
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=payload['prompt'],
            max_tokens = 1000,
            temperature = 0.1,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    
    # Get all .py files in this directory
    file_paths = []
    for file in os.listdir():
        if file.endswith(".py"):
            file_paths.append(file)
    
    # Read the content of each Python file
    file_contents = read_py_files(file_paths)
    
    for file_path, content in file_contents.items():
        print(f"Checking {file_path}")
        
        # Make an API call to OpenAI to check if the code will run
        openai_response = call_openai_api(content)
        
        print(f"Code Review: {openai_response}")
        
        # # If the OpenAI response is not "Pass", rewrite the .py file with the OpenAI response
        # if openai_response.strip() != "Pass" and file_path != "ailinter.py":
        #     with open(file_path, 'w') as f:
        #         f.write(openai_response)
