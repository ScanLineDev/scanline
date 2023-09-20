# AI Linter

### AI-generated error-checking for your AI-generated code 

- Anticipate issues with code before running it. 

- Find subtle issues that may not be obvious at first glance. 

- Check for internal consistency, and for external consistency with the rest of the codebase.

## Usage 

- Set a local `.env` file with your `OPENAI_API_KEY`, or `export OPENAI_API_KEY=xxx`

```bash
# one line automated code review 
reviewme run 

# optional: set the scope 
reviewme run --scope <commit, branch, repo>

```
# New Build Process for global install 
pyinstaller --onefile reviewme/ailinter/ailinter.py

# Build
pip3 install -e .

# Run
reviewme --help to see available commands!

## Update rule style guide 
- Add rule templates to /rule_templates. This text will be included in the prompt to the LLM, so the LLM can evaluate the code according to the style guide you write. 

### Update settings
Update the default rule template and LLM settings in `config.yaml` 

### Future work 
- Retrieve the documentation for all imported libraries
- Trace function calls throughout the codebase


