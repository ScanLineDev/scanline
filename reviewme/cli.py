#!/usr/bin/env python3
from reviewme.ailinter import ailinter 
import click
import logging

logging.basicConfig(level=logging.WARN)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print ("👨🏻‍💻 Starting AI code review on branch")
        ailinter.run("branch", "")
        print ("✅ Code review complete.")

@click.command()
@click.option('--scope', default="branch", help='Scope of code review. Can be "commit", "branch", or "repo". Defaults to "branch"')
@click.option('--file', default="", help='Select a specific file to review. Defaults to all files in scope.')
@click.option('--model', default="gpt-4", help='Specify openai model to use listed @ https://platform.openai.com/docs/models/overview. For example gpt-4-32k supports 4x larger files whereas gpt-3.5-turbo should be faster and >10x cheaper. Defaults to gpt-4.')
def run(scope, file, model):
    if file != "":
        print ("👨🏻‍💻 Starting AI code review on {0}, in {1}".format(scope, file))
    else:
        print ("👨🏻‍💻 Starting AI code review on {0}".format(scope, file))

    ailinter.run(scope, file, model)

cli.add_command(run)

if __name__ == '__main__':
    cli()