# ScanLine (Alpha)

This tool reviews your code using GPT4 and points out ways to impove it, like having an experienced code reviewer on your team. This should not replace you doing good code review, it is meant to assist! 


It'll provide feedback in areas like security, performance, race conditions, consistency, testability, modularity, complexity, error handling, and optimization

This is the V0 release so it may be buggy & design can change suddenly. 
## Install
- Install the latest release of the CLI tool
```bash
bash -c "$(curl -sSL https://raw.githubusercontent.com/ScanLineDev/scanline/main/install.sh)"
```
- Set a local `.env` file with your `OPENAI_API_KEY`, or `export OPENAI_API_KEY=xxx`



## Usage
```bash
# see all available commands
scan --help 

# examples
# check all diffed changed on your current branch compared to main or master
scan

# or only review uncommited changes on the current branch 
scan run --scope commit

# or review all the code in the whole repo
scan run --scope repo

# in addition you can specify a single file. For example here's how to see the changes to the file foo.py across only this last commit
scan run --scope repo --file ./path/to/foo.py

```

# Build with Pip (for testing)
`pip3 install -e .`

Now you can run the CLI as reviewme above. It should auto-update if you change the python code. You may have to run pip3 install -r requirements first
Experimental: You can add rule templates to /rule_templates directory. This text will be included in the prompt to the LLM, so the LLM can evaluate the code according to the style guide you write. 
Experimental: Modify config.yaml to twewak things like temperature, supported filetypes, and how many results to show per category. 

# Contributing
- Feel free to open a PR with your own changes if you'd like to see something added!
- Open an issue if you find any bugs or have an ideas
