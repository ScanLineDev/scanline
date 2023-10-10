#!/usr/bin/env python3
from reviewme.ailinter import ailinter 
import click
import logging
from click_default_group import DefaultGroup
import os

logging.basicConfig(level=logging.DEBUG)

@click.group(cls=DefaultGroup, default='run', default_if_no_args=True)
def cli():
    print("Booting up code review process... ")
    pass

@cli.command()
@click.option('--scope', default="demo", help='Scope of code review. Can be "commit", "branch", "repo", or "demo". Defaults to "demo"')
@click.option('--file', default="", help='Select a specific file to review. Defaults to all files in scope.')
@click.option('--model', default="gpt-4", help='Specify openai model to use listed @ https://platform.openai.com/docs/models/overview. For example gpt-4-32k supports 4x larger files whereas gpt-3.5-turbo should be faster and >10x cheaper. Defaults to gpt-4.')
def run(scope, file, model):
    branch = ailinter.get_current_branch()
    if branch == None:
        print ("👨🏻‍💻 You are not in a git repo. Please run this command in a git repo.")
        return

    # check if OPENAI_API_KEY is not set, if so, exit
    if os.environ.get('OPENAI_API_KEY') == None:
        print ("👨🏻‍💻 An OPENAI_API_KEY was not found. Please set it in your .bashrc or in this terminal session via \'export OPENAI_API_KEY=*****\' and try scanline again.")
        return

    if scope == "branch" and (branch == "main" or branch == "master"):
        print ("👨🏻‍💻 You are on the {0} branch already. Please checkout a different branch to see a review on the branch differences. Or, if you want to compare local changes on your main branch to itself then run \"scanline --scope commit\".".format(branch))
        return

    if file != "":
        print ("👨🏻‍💻 Starting AI code review on {0}, in {1}".format(scope, file))
    else:
        print ("👨🏻‍💻 Starting AI code review on {0} ".format(scope, file))

    ailinter.run(scope, file, model)

if __name__ == '__main__':
    cli()