import click

############ Text Strings ############

answer = ">> Answer"

############ Display Functions ############

# echo lead text
def lecho(text):
    click.secho(click.wrap_text(text), fg="magenta")

# ask a question
def question(text):
    click.echo("")
    click.secho(text, fg="cyan")

# display an informational header
def info(text):
    click.echo("")
    click.secho(text, fg="green")

# display an error
def error(text):
    click.echo("")
    click.ClickException(text).show()

# display a list
def list(text, items, key):
    info(text)
    for x in items:
        if key:
            click.echo("* " + x[key])
        else:
            click.echo("* " + x)

############ Question Functions ############

# choose from a list of options
def options(text, choices, key=None):
    question(text)
    for i, c in enumerate(choices, start=1):
        if key:
            click.echo("[" + str(i) + "] " + c[key])
        else:
            click.echo("[" + str(i) + "] " + c)
    return click.prompt(answer, type=click.IntRange(1, len(choices)))

# ask y/n for whether each of the items should be appended to returned list
def collect(text, items, list, modifier=None):
    question(text)
    for item in items:
        if item not in list:
            label = item
            if modifier:
                label = modifier(item)
            click.secho(label + "? [y/n]", fg="yellow")
            if click.prompt(answer, type=click.Choice(["y","n"])) == "y":
                list.append(item)
    return list

# choose from an int range
def range(text, min, max):
    question(text + " [" + str(min) + "-" + str(max) + "]")
    return click.prompt(answer, type=click.IntRange(min, max))

# confirm y/n
def confirm(text):
    question(text + " [y/n]")
    return click.prompt(answer, type=click.Choice(["y","n"]))

# freeform
def blurb(text):
    question(text)
    return click.prompt(answer)
