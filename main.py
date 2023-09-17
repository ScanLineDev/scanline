#!/usr/bin/env python3
from ailinter import ailinter 
import click

@click.command()
@click.option('--scope', default="branch", help='Scope of code review. Can be "commit", "branch", or "repo". Defaults to "branch"')
def run(scope):
    print ("👨🏻‍💻 Starting AI code review on {0}".format(scope))
    ailinter.run(scope)
    print ("✅ Code review complete.")
    
if __name__ == '__main__':
    run()