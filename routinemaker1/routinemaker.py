

from pyfiglet import Figlet
import routine
import prompt
import exercises
import xlsxwriter

@prompt.click.command()
def main():
    """Generate custom strength, cardio, and HIIT exercise routines using parametric curves"""

    # 스크린 장면
    prompt.click.clear()
    prompt.click.echo(Figlet(font="standard").renderText("Routinemaker"))
    prompt.lecho("Routinemaker는 파라메트릭 공선을 사용하여 strength, cardio, 그리고 HIIT 운동 루틴을 생성한다. 시작해보자!")

    # 루틴 타입 선택
    type = prompt.options("어떤 유형의 루틴을 생성하시겠습니까?", ["Strength", "Cardio", "HIIT"])

    # 강도 루틴 구성
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
