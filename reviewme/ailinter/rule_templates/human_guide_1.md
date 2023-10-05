# SuperCo Style Guide 
### PEP Compliance
PEP 8: Follow the PEP 8 style guide for Python code.
PEP 20: Follow the Zen of Python (PEP 20) for general programming philosophy.
PEP 257: Adhere to PEP 257 for writing good docstrings.

### Naming Conventions
Modules: Short, all-lowercase names. Prefer underscores if it improves readability.
Correct: my_module.py
Avoid: MyModule.py

### Imports
Import Ordering: Standard libraries first, third-party libraries next, and application-specific imports last.

Explicit Imports: Use explicit imports rather than wildcards.
Correct: from os import path
Avoid: from os import *