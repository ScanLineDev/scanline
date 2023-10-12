# ScanLine (Parea-AI)

Catch bugs before they hurt. ScanLine reviews your code with GPT-4 and shows you how to improve it, like having an
experienced code reviewer with you 24/7.

ScanLine is an **AI-based tool** to quickly check your commit, branch, or entire repo for:

- [x] 🏁 race conditions
- [x] 🔒 security gaps
- [x] 💡 inconsistent logic
- [x] 🚀 performance
- [x] ☑️ consistency
- [x] ⚙️ optimization
- [x] ⚠️ error handling

## Why use Scanline?

_“Scanline already saved us a few weeks on prod outages by catching race conditions”_ - CTO, ML infrastructure company

_“I used to spend 5+ hours a day reviewing my team's code; now it's less than 1, while also uncovering more
high-priority updates”_ - Eng Manager

_“My team started complementing the quality of my PRs”_ - SWE

_"Code gen and automatic PRs are still unreliable, but Scanline's code review is immediately useful and actionable."_ -
Friend who's tried a lot of AI tools

## Local development for testing :

Experimental: You can add rule templates to /rule_templates directory. This text will be included in the prompt to the
LLM, so the LLM can evaluate the code according to the style guide you write.

Experimental: Modify config.yaml to tweak things like temperature, supported filetypes, and how many results to show per
category.