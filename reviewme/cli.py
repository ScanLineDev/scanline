#!/usr/bin/env python3
from reviewme.ailinter import ailinter 
import click
import logging
from click_default_group import DefaultGroup

logging.basicConfig(level=logging.DEBUG)

@click.group(cls=DefaultGroup, default='run', default_if_no_args=True)
def cli():
    print("Booting up code review process... ")
    pass

@cli.command()
@click.option('--scope', default="branch", help='Scope of code review. Can be "commit", "branch", or "repo". Defaults to "branch"')
@click.option('--file', default="", help='Select a specific file to review. Defaults to all files in scope.')
@click.option('--model', default="gpt-4", help='Specify openai model to use listed @ https://platform.openai.com/docs/models/overview. For example gpt-4-32k supports 4x larger files whereas gpt-3.5-turbo should be faster and >10x cheaper. Defaults to gpt-4.')
def run(scope, file, model):
    branch = ailinter.get_current_branch()
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