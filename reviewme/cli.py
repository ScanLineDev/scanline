#!/usr/bin/env python3
from .ailinter import ailinter 
import click
import logging

logging.basicConfig(level=logging.DEBUG)

@click.group()
def cli():
    pass

@click.command()
@click.option('--scope', default="branch", help='Scope of code review. Can be "commit", "branch", or "repo". Defaults to "branch"')
@click.option('--file', default="", help='Select a specific file to review. Defaults to all files in scope.')
def run(scope, file):
    if file != "":
        print ("👨🏻‍💻 Starting AI code review on {0}, in {1}".format(scope, file))
    else:
        print ("👨🏻‍💻 Starting AI code review on {0}".format(scope, file))

    ailinter.run(scope, file)
    print ("✅ Code review complete.")

cli.add_command(run)

if __name__ == '__main__':
    cli()