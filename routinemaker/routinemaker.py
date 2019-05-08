from pyfiglet import Figlet
from . import routine
from . import prompt
from . import exercises
import xlsxwriter

@prompt.click.command()
def main():
    """Generate custom strength, cardio, and HIIT exercise routines using parametric curves"""

    # splash screen
    prompt.click.clear()
    prompt.click.echo(Figlet(font="standard").renderText("Routinemaker"))
    prompt.lecho("Routinemaker generates strength, cardio, and HIIT exercise routines using parametric curves. Let's get started!")

    # choose routine type
    type = prompt.options("What type of routine do you want to create?", ["Strength", "Cardio", "HIIT"])

    # configure strength routines
    if type == 1:
        # check for equipment and narrow exercises to pool
        equipment = ["Bodyweight"]
        prompt.collect("What type of equipment do you have access to?", exercises.unique(exercises.strength, "Variations"), equipment, lambda x: x + "s")
        pool = exercises.filter(exercises.strength, equipment, "Variations")
        # choose random or manual population of exercises
        path = prompt.options("How would you like to choose the exercises for your routine?", ["Start with a random list of exercises", "Manually add exercises"])
        # start with a random list of exercises
        if path == 1:
            # check for muscle groups of interest and narrow exercises down to candidates
            muscles = []
            while len(muscles) < 1:
                prompt.collect("Which muscle groups do you want to train?", exercises.unique(pool, "Group"), muscles)
                if len(muscles) < 1:
                    prompt.error("You must pick at least one muscle group.")
            cart = routine.randomize(exercises.filter(pool, muscles, "Group"))
        # manually add exercises
        elif path == 2:
            cart = routine.shop(pool)
        # add, remove, swap, or reorder exercises in cart
        cart = routine.edit(cart, pool)

    # configure cardio routines
    elif type == 2:
        # select activity
        activities = list(exercises.unique(exercises.cardio, "Group"))
        activity = activities[prompt.options("Which cardio activity would you like to do?", activities)-1]
        # get pool of exercises
        pool = exercises.filter(exercises.cardio, activity, "Group")
        # choose specific exercise
        if len(pool) > 1:
            cart = [pool[prompt.options("Which specific exercise would you like to work on?", pool, key="Name")-1]]
        else:
            cart = [pool[0]]

    # configure HIIT routines
    elif type == 3:
        # choose random or manual population of exercises
        path = prompt.options("How would you like to choose the exercises for your routine?", ["Start with a random list of exercises", "Manually add exercises"])
        # start with a random list of exercises
        if path == 1:
            cart = routine.randomize(exercises.HIIT)
        # manually add exercises
        elif path == 2:
            cart = routine.shop(exercises.HIIT)
        # add, remove, swap, or reorder exercises in cart
        cart = routine.edit(cart, exercises.HIIT)

    # get parameters
    parameters = routine.parameters(cart)

    # generate routine
    data = routine.calculate(parameters)

    # output routine as Excel spreadsheet
    routine.output(data)

if __name__ == '__main__':
    main()
