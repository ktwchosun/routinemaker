from . import prompt
from . import exercises
import numpy as np
import random
import xlsxwriter

############ Cart Functions ############

# add or swap exercises
def add(candidates, cart, muscles, i=None):
    if muscles:
        # pick muscle group to browse exercises
        choices = exercises.filter(candidates, muscles[prompt.options("Pick a muscle group to browse exercises to add:", muscles, None)-1], key="Group")
    else:
        choices = candidates
    # choose exercises from list
    choice = choices[prompt.options("Which exercise would you like to add?", choices, key="Name")-1]
    # add or swap the choice and return the cart
    if i:
        cart[i] = choice
    else:
        cart.append(choice)
    return cart

# reorder exercises
def reorder(cart):
    # choose exercise to move
    i = prompt.options("Which exercise would you like to move?", cart, key="Name")-1
    choice = [cart[i]]
    cart = cart[:i] + cart[i+1:]
    # choose where to put the exercise
    i = prompt.options("Which exercise would you like to move it before?", cart, key="Name")-1
    return cart[:i] + choice + cart[i:]

# get random list of exercises
def randomize(candidates):
    # choose number of exercises in routine
    size = prompt.range("How many exercises do you want in your routine?", 1, min(len(candidates),12))
    cart = exercises.random.sample(candidates, size)
    # display exercises in cart
    prompt.list("Exercises in routine:", cart, "Name")
    return cart

# manually select exercises
def shop(pool):
    # set up the cart of selected exercises
    cart = []
    # loop through exercise selection
    while(True):
        # create candidates list and get all the muscles
        candidates = [p for p in pool if p not in cart]
        if len(candidates) > 0:
            muscles = list(exercises.unique(candidates, "Group"))
            # choose an exercise to add to cart
            cart = add(candidates, cart, muscles, None)
            # display exercises in cart
            prompt.list("Exercises in routine:", cart, "Name")
            # add another exercise or move on
            if prompt.confirm("Would you like to add another exercise?") == "n":
                break
        else:
            prompt.error("There are no more exercises that can be added.")
            break
    return cart

# edit exercises
def edit(cart, pool):
    if prompt.confirm("Do you need to edit or reorder the exercises in your routine?") == "y":
        while(True):
            # reset candidates list and get all the muscles
            candidates = [p for p in pool if p not in cart]
            muscles = list(exercises.unique(candidates, "Group"))
            # check which task needs to be done
            option = prompt.options("What would you like to do?", ["Add exercise", "Remove exercise", "Swap exercise", "Reorder exercise"])
            # add exercise
            if option == 1:
                if len(candidates) > 0:
                    # choose an exercise to add to cart
                    cart = add(candidates, cart, muscles)
                    # display exercises in cart
                    prompt.list("Exercises in routine:", cart, "Name")
                else:
                    prompt.error("There are no more exercises that can be added.")
            # remove exercise
            elif option == 2:
                # remove chosen exercise from cart
                del cart[prompt.options("Which exercise would you like to remove?", cart, key="Name")-1]
                # display exercises in cart
                prompt.list("Exercises in routine:", cart, "Name")
            # swap exercise
            elif option == 3:
                if len(candidates) > 0:
                    # choose an exercise to swap into cart
                    cart = add(candidates, cart, muscles, i=prompt.options("Which exercise would you like to swap?", cart, key="Name")-1)
                    # display exercises in cart
                    prompt.list("Exercises in routine:", cart, "Name")
                else:
                    prompt.error("There are no more exercises that can be swapped in.")
            # reorder exercise
            elif option == 4:
                cart = reorder(cart)
                # display exercises in cart
                prompt.list("Exercises in routine:", cart, "Name")
            # do more to cart or move on
            if prompt.confirm("Do you need to edit or reorder more exercises in your routine?") == "n":
                break
    return cart


############ Parameter Functions ############

# configure start and goal for activities
def configure(cart):
    # configure each activity
    for activity in cart:
        # configure variation
        if len(activity["Variations"]) > 1:
            activity["Variations"] = [activity["Variations"][prompt.options("Which variation of " + activity["Name"].upper() + " do you plan on doing?", activity["Variations"])-1]]
        activity["Name"] = activity["Variations"][0] + " " + activity["Name"]
        # configure reps or duration
        activity["Start"] = prompt.range("How many continuous " + activity["Unit"] + " of " + activity["Name"].upper() + " are you currently comfortable with?", activity["Min"], activity["Max"])
        activity["Goal"] = prompt.range("How many continuous " + activity["Unit"] + " of " + activity["Name"].upper() + " is your goal?", activity["Start"], activity["Max"])
        # configure weights
        if activity["Type"] == "Strength" and activity["Variations"][0] != "Bodyweight":
            activity["Start Weight"] = prompt.range("What weight are you currently using for " + activity["Name"].upper() + "? (lbs)", 0, 500)
            activity["Goal Weight"] = prompt.range("What's your goal weight for " + activity["Name"].upper() + "? (lbs)", activity["Start Weight"], 500)
    return cart

# configure parameters
def parameters(cart):
    # set array of curves to be processed in generate()
    curves = ["Linear", "Exponential", "Logarithmic"]
    # populate parameters
    params = dict()
    params["Weeks"] = prompt.range("How many weeks would you like your routine to last?", 3, 12)
    params["Days"] = prompt.range("How many days per week are you planning on exercising?", 2, 6)
    params["Cart"] = configure(cart)
    if cart[0]["Type"] == "Strength" or cart[0]["Type"] == "HIIT":
        params["Minsets"] = prompt.range("What's the mininum number of sets you'd like to do for each exercise?", 2, 12)
        params["Maxsets"] = prompt.range("What's the maximum number of sets you'd like to do for each exercise?", params["Minsets"], 12)
    elif cart[0]["Type"] == "Cardio":
        params["Maxsets"] = prompt.range("What's the maximum number of intervals you want in your routine?", 1, 12)
        params["Seed"] = prompt.range("Please choose a random number to seed the routine.", 1, 1000)
    params["Curve"] = curves[prompt.options("What type of curve do you want to use to create your routine?", curves)-1]
    return params

############ Calculation Functions ############

# return y value for x given linear curve that goes through p1 and p2
def linear(p1, p2, x):
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    b = p1[1]-m*p1[0]
    y = m*x+b
    return max(y,0)

# return y value for x given exponential curve that goes through p1 and p2
def exponential(p1, p2, x):
    xvals = np.array([p1[0], p2[0]])
    yvals = np.array([p1[1]+1, p2[1]+1])
    params = np.polyfit(xvals, np.log(yvals), 1)
    y = np.exp(params[1])*np.exp(params[0]*(x))-1
    return max(y,0)

# return y value for x given logarithmic curve that goes through p1 and p2
def logarithmic(p1, p2, x):
    xvals = np.array([p1[0]+1, p2[0]+1])
    yvals = np.array([p1[1], p2[1]])
    params = np.polyfit(np.log(xvals), yvals, 1)
    y = params[0]*np.log(x+1)+params[1]
    return max(y,0)

# returns a random number within the configured range
def fuzzy():
    return random.uniform(0.7, 1.5)

# round to the nearest n
def nround(num, n=1):
    result = round(num/n)*n
    if n >= 1:
        return int(result)
    return result

############ Output Functions ############

# generate routine as an array of activities with days
def calculate(parameters):
    routine = []
    # seed random numbers
    if "Seed" in parameters:
        random.seed(parameters["Seed"])
    # generate each exercise
    for activity in parameters["Cart"]:
        exercise = dict()
        exercise["Name"] = activity["Name"]
        exercise["Type"] = activity["Type"]
        exercise["Unit"] = activity["Unit"]
        exercise["Maxsets"] = parameters["Maxsets"]
        exercise["Days"] = []
        # generate each day
        for w in range(1, parameters["Weeks"]+1):
            for d in range(1, parameters["Days"]+1):
                day = dict()
                day["Week"] = w
                day["Day"] = d
                day["Sequence"] = (w-1)*parameters["Days"]+d
                day["Progress"] = day["Sequence"]/(parameters["Weeks"]*parameters["Days"])
                # calculate curves for strength and HIIT
                if exercise["Type"] == "Strength" or exercise["Type"] == "HIIT":
                    # linear
                    if parameters["Curve"] == "Linear":
                        day["Sets"] = nround(linear([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(linear([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(linear([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                    # exponential
                    elif parameters["Curve"] == "Exponential":
                        day["Sets"] = nround(exponential([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(exponential([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(exponential([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                    # logarithmic
                    elif parameters["Curve"] == "Logarithmic":
                        day["Sets"] = nround(logarithmic([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(logarithmic([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(logarithmic([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                # calculate curves for Cardio
                elif exercise["Type"] == "Cardio":
                    # linear
                    if parameters["Curve"] == "Linear":
                        day["Target"] = nround(linear([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(linear([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # exponential
                    elif parameters["Curve"] == "Exponential":
                        day["Target"] = nround(exponential([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(exponential([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # logarithmic
                    elif parameters["Curve"] == "Logarithmic":
                        day["Target"] = nround(logarithmic([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(logarithmic([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # first day is always overwritten with max intervals
                    if day["Sequence"] == 1:
                        day["Intervals"] = parameters["Maxsets"]
                    # create the segments
                    if day["Progress"] == 1:
                        # last day is always the goal
                        day["Segments"] = [activity["Goal"]]
                    else:
                        # otherwise slightly randomize intervals
                        day["Segments"] = []
                        for i in range(1, day["Intervals"]+1):
                            day["Segments"].append(nround(day["Target"]/day["Intervals"]*fuzzy(), activity["Step"]))
                exercise["Days"].append(day)
        routine.append(exercise)
    return routine

# outputs routine as a spreadsheet
def output(routine):
    # get filename
    filename = prompt.blurb("What do you want to name the output file? (ie: routine.xlsx)")
    if not ".xlsx" in filename:
        filename = filename + ".xlsx"
    # start writing spreadsheet
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    # set up row and column iterators
    row = 0
    col = 0
    # set up formats
    title = workbook.add_format({"bold": True, "align": "center", "font_color": "#ffffff", "bg_color": "#333333", "border": 1})
    dark = workbook.add_format({"align": "center", "font_color": "#ffffff", "bg_color": "#666666", "border": 1})
    gray = workbook.add_format({"align": "center", "bg_color": "#cccccc", "border": 1})
    light = workbook.add_format({"align": "center", "bg_color": "#eeeeee", "border": 1})
    white = workbook.add_format({"align": "center", "font_color": "#777777", "bg_color": "#ffffff", "border": 1})
    # format exercises
    for exercise in routine:
        # format strength and HIIT
        if exercise["Type"] == "Strength" or exercise["Type"] == "HIIT":
            worksheet.merge_range(row, col, row, col+exercise["Maxsets"]+1, exercise["Name"], title)
            row += 1
            worksheet.write(row, col, "Day", dark)
            col += 1
            worksheet.write(row, col, exercise["Unit"].title(), dark)
            col += 1
            for i in range(0, exercise["Maxsets"]):
                worksheet.write(row, col, "Set " + str(i+1), dark)
                col += 1
            row += 1
            col = 0
            for day in exercise["Days"]:
                worksheet.write(row, col, day["Sequence"], gray)
                col += 1
                worksheet.write(row, col, day["Reps"], light)
                col += 1
                for i in range(0, exercise["Maxsets"]):
                    if i < day["Sets"]:
                        if "Weight" in day:
                            worksheet.write(row, col, day["Weight"], white)
                        else:
                            worksheet.write(row, col, "", white)
                    else:
                        worksheet.write(row, col, "", gray)
                    col += 1
                row += 1
                col = 0
        # format cardio
        elif exercise["Type"] == "Cardio":
            worksheet.merge_range(row, col, row, col+exercise["Maxsets"]+1, exercise["Name"] + " (" + exercise["Unit"].title() + ")", title)
            row += 1
            worksheet.write(row, col, "Day", dark)
            col += 1
            worksheet.write(row, col, "Total", dark)
            col += 1
            for i in range(0, exercise["Maxsets"]):
                worksheet.write(row, col, "Interval " + str(i+1), dark)
                col += 1
            row += 1
            col = 0
            for day in exercise["Days"]:
                worksheet.write(row, col, day["Sequence"], gray)
                col += 1
                worksheet.write(row, col, sum(day["Segments"]), light)
                col += 1
                for i in range(0, exercise["Maxsets"]):
                    if i < len(day["Segments"]):
                        worksheet.write(row, col, day["Segments"][i], white)
                    else:
                        worksheet.write(row, col, "", gray)
                    col += 1
                row += 1
                col = 0
    workbook.close()
    prompt.info(filename)
    return True
