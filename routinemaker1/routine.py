
import prompt
import exercises
import numpy as np
import random
import xlsxwriter  #엑셀 작업 자동화

############ 카트 기능들 ############

# 운동추가 또는 교환
def add(candidates, cart, muscles, i=None):
    if muscles:
        # 운동 근육 그룹 선택
        choices = exercises.filter(candidates, muscles[prompt.options("추가할 운동 근육 그룹을 선택하시오:", muscles, None)-1], key="Group")
    else:
        choices = candidates
    # 리스트에서 운동 선택
    choice = choices[prompt.options("어떤 운동을 추가 하시겠습니까?", choices, key="Name")-1]
    # 선택 항목을 추가 또는 교환하고 카트 반환
    if i:
        cart[i] = choice
    else:
        cart.append(choice)
    return cart

# 운동 재설정
def reorder(cart):
    # 실행할 운동 선택
    i = prompt.options("어떠한 운동을 옮기시겠습니까?", cart, key="Name")-1
    choice = [cart[i]]
    cart = cart[:i] + cart[i+1:]
    # 이전에 실행할 운동 선택
    i = prompt.options("이전에 어떤 운동으로 옮기고 싶으세요?", cart, key="Name")-1
    return cart[:i] + choice + cart[i:]

# 무작위로 운동 리스트 얻기
def randomize(candidates):
    # 루틴 내에서 운동 개수 선택
    size = prompt.range("루틴 내에서 얼마나 많은 운동개수를 원합니까?", 1, min(len(candidates),12))
    cart = exercises.random.sample(candidates, size)
    # 운동 종류 표시
    prompt.list("루틴 운동:", cart, "Name")
    return cart

# 운동 수동 선택
def shop(pool):
    # 선택된 운동 카트에 준비
    cart = []
    # 루프를 통한 운동 선택
    while(True):
        #  후보리스트 생성,
        candidates = [p for p in pool if p not in cart]
        if len(candidates) > 0:
            muscles = list(exercises.unique(candidates, "Group"))
            # 카트에 추가할 운동 선택
            cart = add(candidates, cart, muscles, None)
            # 카트에 운동 표시
            prompt.list("루틴 운동:", cart, "Name")
            # 또다른 운동추가 또는 다음으로 이동
            if prompt.confirm("또 다른 운동을 추가하시겠습니까?") == "n":
                break
        else:
            prompt.error("추가할 수 있는 운동이 없습니다.")
            break
    return cart

# 운동 수정
def edit(cart, pool):
    if prompt.confirm("운동 루틴에서 수정하거나 재설정을 원하시나요? ") == "y":
        while(True):
            # 후보리스트 재설정
            candidates = [p for p in pool if p not in cart]
            muscles = list(exercises.unique(candidates, "Group"))
            # 필요로 하는 일 체크
            option = prompt.options("무엇을 하길 원합니까?", ["운동 추가", "운동 삭제", "운동 변경", "운동 재설정"])
            # 운동추가
            if option == 1:
                if len(candidates) > 0:
                    # 카트에 추가할 운동 선택
                    cart = add(candidates, cart, muscles)
                    # 카트에 운동 표시
                    prompt.list("운동 루틴:", cart, "Name")
                else:
                    prompt.error("더 이상 추가할 수 있는 운동이 없습니다.")
            # 운동 삭제
            elif option == 2:
                # 카트에 선택된 운동 삭제
                del cart[prompt.options("어떤 운동을 제거 하시겠습니까?", cart, key="Name")-1]
                # 카트에 운동 표시
                prompt.list("운동 루틴:", cart, "Name")
            # 운동 변경
            elif option == 3:
                if len(candidates) > 0:
                    # 카트에서 변경할 운동 선택
                    cart = add(candidates, cart, muscles, i=prompt.options("어떤 운동을 변경 하시겠습니까?", cart, key="Name")-1)
                    # 카트에 운동 표시
                    prompt.list("운동 루틴:", cart, "Name")
                else:
                    prompt.error("더 이상 변경할 수 있는 운동이 없습니다.")
            # 운동 재설정
            elif option == 4:
                cart = reorder(cart)
                # 카트에 운동 표시
                prompt.list("운동 루틴:", cart, "Name")
            # do more to cart or move on
            if prompt.confirm("운동 루틴에서 수정하거나 재설정을 원하시나요?") == "n":
                break
    return cart


############ 매개 변수 함수 ############

# 활동 시작 및 목표 구성
def configure(cart):
    # 각 활동 구성
    for activity in cart:
        # 변형 구성
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