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
    Please say if you anticipate any issues when running it.
    If it looks OK, respond with the word 'Pass', and nothing else.
    If not, then please respond with a description of the issues, 
    plans for solving them, and updated suggested code.
    """
    payload = {
        "prompt": instructions + "\n\n" + code,
        "max_tokens": 500
    }
    
    # Make the actual API call here
    # Replace "your_openai_api_key_here" with your actual OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=payload['prompt'],
            max_tokens=payload['max_tokens']
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":

    # get all .py file in this directory 
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
        
        print(f"Code review: {openai_response}")
