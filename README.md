# ScanLine (Alpha)

Catch bugs before they hurt. ScanLine reviews your code with GPT-4 and shows you how to impove it, like having an experienced code reviewer with you 24/7. 

ScanLine is an **AI-based CLI tool** to quickly check your commit, branch, or entire repo for: 
- [x] race conditions
- [x] security gaps
- [x] inconsistent logic
- [x] reliability
- [x] consistency
- [x] optimization
- [x] error handling

## Why use Scanline? 

_“Scanline already saved us a few weeks on prod outages by catching race conditions”_ - CTO, ML infrastructure company 

_“I used to spend 5+ hours a day reviewing my team's code; now that's less than 1”_ - Eng Manager 

_“My team started complementing the quality of my PRs”_ - SWE

_"Code gen and automatic PRs are still unreliable, but Scanline's code review is immediately useful and actionable."_ - Friend who's tried a lot of AI tools 

# Quick Start - Install

**For Apple M1+ Silicon (ARM64):**
```bash
bash -c "$(curl -sSL https://raw.githubusercontent.com/ScanLineDev/scanline/main/install.sh)"
```

**For Apple Intel (x86):**
```bash
bash -c "$(curl -sSL https://raw.githubusercontent.com/ScanLineDev/scanline/main/install_x86.sh)"
```

then: 

`cd` into the repo and branch to review. Run `scanline`. 

(If you happen to not to set an OpenAI key during the install guide, then set a local `.env` file with your `OPENAI_API_KEY`, or `export OPENAI_API_KEY=xxx`.)

## 1-minute Demo 
[scanline video demo](https://github.com/ScanLineDev/scanline/assets/2404105/43a46cc2-65f4-40ef-a7c0-b3d60cabdadb)

_(Click video to play)_

## How To Use 
```bash
# see all available commands
scanline --help 

# check all diffed changes on your current branch compared to main or master
scanline

# only review uncommited changes on the current branch 
scanline --scope commit

# review all the code in the whole repo
scanline --scope repo

# in addition you can specify a single file. For example, here's how to see the changes to the file foo.py across only this last commit
scanline --scope repo --file ./path/to/foo.py

```

#### Notes 
This should not replace you doing good code review--it is meant to assist! 

This is the V0 release, so it may be buggy & design may change quickly. 

# Contributing
- Feel free to open a PR with your own changes if you'd like to see something added!
- Open an issue if you find any bugs or have an ideas

## Local development for testing (build with pip): 
`pip3 install -e .`

Now you can run the CLI as `reviewme` above. It should auto-update if you change the python code. You may have to run `pip3 install -r requirements` first

Experimental: You can add rule templates to /rule_templates directory. This text will be included in the prompt to the LLM, so the LLM can evaluate the code according to the style guide you write. 

Experimental: Modify config.yaml to tweak things like temperature, supported filetypes, and how many results to show per category. 


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
