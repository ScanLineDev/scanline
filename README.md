# AI Linter

### AI-generated error-checking for your AI-generated code 

- Anticipate issues with code before running it. 

- Find subtle issues that may not be obvious at first glance. 

- Check for internal consistency, and for external consistency with the rest of the codebase.

## Usage 

```py
from modules import ailinter 

def main():
    print ("Your program here...")

if __name__ == "__main__":   
    ailinter.run()          # --> run AILinter 
    main()

```


### Future work 

- Retrieve the documentation for all imported libraries
- Trace function calls throughout the codebase
