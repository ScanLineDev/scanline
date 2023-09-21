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
# Build and Install 
1. Generate a build with the `pyinstaller` package:

`pyinstaller aicli-build.spec`

2. This will generate a build in `dist/ailinter-build`. Move that to the public `aicli` repo using Github Releases. Update the referenced build file in `install.sh`

3. Users can now install AI CLI with curl with the command:
`curl -sSL https://raw.githubusercontent.com/stephenkfrey/ailinter/reviewme/install.sh | sudo bash`

# Build with Pip (for testing)
`pip3 install -e .`

# Run
reviewme --help to see available commands!

## Update rule style guide 
- Add rule templates to /rule_templates. This text will be included in the prompt to the LLM, so the LLM can evaluate the code according to the style guide you write. 

### Update settings
Update the default rule template and LLM settings in `config.yaml` 

### Future work 
- Retrieve the documentation for all imported libraries
- Trace function calls throughout the codebase


