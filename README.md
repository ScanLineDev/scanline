## Why use Scanline? 

_“Scanline already saved us a few weeks on prod outages by catching race conditions”_ - CTO, ML infrastructure company 

_“That issue would have hurt us bad in the future”_ - SWE, AI startup

_“I look smarter to my team”_ - anon

_“I can finally augment myself!”_ - Ray, eng manager 

_“I can replace my eng manager!”_ - SWE (works with Ray)

_“I can review my teams PRs in seconds”_ - Ray, eng manager

_"Code gen and automatic PRs are still unreliable, but Scanline's code review is immediately useful and actionable."_ - Friend who's tried hundreds of AI tools 


# ScanLine (Alpha)

This tool reviews your code using GPT4 and points out ways to impove it, like having an experienced code reviewer on your team. This should not replace you doing good code review, it is meant to assist! 

**Privacy**

Code is sent to OpenAI directly with your OpenAI key **(your code is only shared with OpenAI, not us)** 

It'll provide feedback in areas like security, performance, race conditions, consistency, testability, modularity, complexity, error handling, and optimization

This is the V0 release so it may be buggy & design can change suddenly. 
## Install
- Install the latest release of the CLI tool

**For Apple M1+ Silicon (ARM64):**
```bash
bash -c "$(curl -sSL https://raw.githubusercontent.com/ScanLineDev/scanline/main/install.sh)"
```

**For Apple Intel (x86):**
```bash
bash -c "$(curl -sSL https://raw.githubusercontent.com/ScanLineDev/scanline/main/install_x86.sh)"
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
scan --scope commit

# or review all the code in the whole repo
scan --scope repo

# in addition you can specify a single file. For example here's how to see the changes to the file foo.py across only this last commit
scan --scope repo --file ./path/to/foo.py

```

# Build with Pip (for testing)
`pip3 install -e .`

Now you can run the CLI as reviewme above. It should auto-update if you change the python code. You may have to run pip3 install -r requirements first
Experimental: You can add rule templates to /rule_templates directory. This text will be included in the prompt to the LLM, so the LLM can evaluate the code according to the style guide you write. 
Experimental: Modify config.yaml to twewak things like temperature, supported filetypes, and how many results to show per category. 

# Contributing
- Feel free to open a PR with your own changes if you'd like to see something added!
- Open an issue if you find any bugs or have an ideas

## Currently supported languages:
```
Python - .py
JavaScript - .js
TypeScript - .ts
Shell, Bash - .sh, .bash
Rust - .rs
Go - .go
C - .c
C++ - .cpp, .cc, .cxx, .c++
C# - .cs
Objective-C - .m, .mm
R - .r
Ruby - .rb
PHP - .php
Java - .java
Swift - .swift
Kotlin - .kt, .kts
Scala - .scala
Perl - .pl, .pm
Lua - .lua
Groovy - .groovy, .grvy, .gy, .gvy
```
