
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
        # 개수와 세트 수 설정
        activity["Start"] = prompt.range(activity["Name"].upper() + "연속 몇개까지 쉽게 할 수 있습니까?", activity["Min"], activity["Max"])
        activity["Goal"] = prompt.range(activity["Name"].upper() + "연속 몇개까지 너의 목표입니까?", activity["Start"], activity["Max"])
        # 무게 설정
        if activity["Type"] == "Strength" and activity["Variations"][0] != "Bodyweight":
            activity["Start Weight"] = prompt.range("현재 사용 중인 무게는 얼마입니까 " + activity["Name"].upper() + "? (lbs)", 0, 500)
            activity["Goal Weight"] = prompt.range("너의 목표 무게는 얼마입니까 " + activity["Name"].upper() + "? (lbs)", activity["Start Weight"], 500)
    return cart

# 매개 변수 구성
def parameters(cart):
    # 생성 시 처리할 원곡선 배열 설정()
    curves = ["선형", "지수", "로그"]
    # 매개변수 채우기
    params = dict()
    params["Weeks"] = prompt.range("당신의 루틴이 몇주동안 지속되기를 원합니까?", 3, 12)
    params["Days"] = prompt.range("당신은 일주일에 몇일 운동할 계획입니까?", 2, 6)
    params["Cart"] = configure(cart)
    if cart[0]["Type"] == "Strength" or cart[0]["Type"] == "HIIT":
        params["Minsets"] = prompt.range("각 운동에 대해 수행할 최소 세트 수는 얼마입니까?", 2, 12)
        params["Maxsets"] = prompt.range("각 운동에 대해 수행할 최대 세트 수는 얼마입니까?", params["Minsets"], 12)
    elif cart[0]["Type"] == "Cardio":
        params["Maxsets"] = prompt.range("너의 루틴에서 최대 간격 수는 몇 번입니까?", 1, 12)
        params["Seed"] = prompt.range("루틴을 시드할 임의의 숫자를 선택해주세요.", 1, 1000)
    params["Curve"] = curves[prompt.options("루틴을 만드는데 사용하기 원하는 곡선 유형은 무엇입니까?", curves)-1]
    return params

############ 계산 기능들 ############

# p1과 p2를 통과하는 주어진 선형 곡선에 대한 y 값 반환
def linear(p1, p2, x):
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    b = p1[1]-m*p1[0]
    y = m*x+b
    return max(y,0)

# p1과 p2를 통과하는 주어진 지수 곡선에 대한 y 반환 값
def exponential(p1, p2, x):
    xvals = np.array([p1[0], p2[0]])
    yvals = np.array([p1[1]+1, p2[1]+1])
    params = np.polyfit(xvals, np.log(yvals), 1)
    y = np.exp(params[1])*np.exp(params[0]*(x))-1
    return max(y,0)

# p1과 p2를 통과하는 x의 주어진 로그 곡선에 대한 y 값 반환
def logarithmic(p1, p2, x):
    xvals = np.array([p1[0]+1, p2[0]+1])
    yvals = np.array([p1[1], p2[1]])
    params = np.polyfit(np.log(xvals), yvals, 1)
    y = params[0]*np.log(x+1)+params[1]
    return max(y,0)

# 구성된 범위 내의 임의의 숫자를 반환
def fuzzy():
    return random.uniform(0.7, 1.5)

# n에 가깝게 반올림
def nround(num, n=1):
    result = round(num/n)*n
    if n >= 1:
        return int(result)
    return result

############ 출력 기능들 ############

# 일 단위의 활동 배열로 루틴 생성
def calculate(parameters):
    routine = []
    # 랜덤 숫자 시드
    if "Seed" in parameters:
        random.seed(parameters["Seed"])
    # 각각의 운동 생성
    for activity in parameters["Cart"]:
        exercise = dict()
        exercise["Name"] = activity["Name"]
        exercise["Type"] = activity["Type"]
        exercise["Unit"] = activity["Unit"]
        exercise["Maxsets"] = parameters["Maxsets"]
        exercise["Days"] = []
        # 각 날짜 생성
        for w in range(1, parameters["Weeks"]+1):
            for d in range(1, parameters["Days"]+1):
                day = dict()
                day["Week"] = w
                day["Day"] = d
                day["Sequence"] = (w-1)*parameters["Days"]+d
                day["Progress"] = day["Sequence"]/(parameters["Weeks"]*parameters["Days"])
                # strength 및 HIIT에 대한 곡선 계산
                if exercise["Type"] == "Strength" or exercise["Type"] == "HIIT":
                    # 선형
                    if parameters["Curve"] == "Linear":
                        day["Sets"] = nround(linear([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(linear([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(linear([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                    # 지수
                    elif parameters["Curve"] == "Exponential":
                        day["Sets"] = nround(exponential([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(exponential([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(exponential([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                    # 로그
                    elif parameters["Curve"] == "Logarithmic":
                        day["Sets"] = nround(logarithmic([0,parameters["Minsets"]], [1,parameters["Maxsets"]], day["Progress"]))
                        day["Reps"] = nround(logarithmic([0,activity["Start"]], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        if "Start Weight" in activity:
                            day["Weight"] = nround(logarithmic([0,activity["Start Weight"]], [1,activity["Goal Weight"]], day["Progress"]), 5)
                # Cardio에 대한 곡선 계산
                elif exercise["Type"] == "Cardio":
                    # 선형
                    if parameters["Curve"] == "Linear":
                        day["Target"] = nround(linear([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(linear([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # 지수
                    elif parameters["Curve"] == "Exponential":
                        day["Target"] = nround(exponential([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(exponential([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # 로그
                    elif parameters["Curve"] == "Logarithmic":
                        day["Target"] = nround(logarithmic([0,min(activity["Start"]*2, activity["Goal"])], [1,activity["Goal"]], day["Progress"]), activity["Step"])
                        day["Intervals"] = parameters["Maxsets"]-nround(logarithmic([0,1], [1,parameters["Maxsets"]], day["Progress"]))+1
                    # 첫날은 항상 최대간격으로 설정
                    if day["Sequence"] == 1:
                        day["Intervals"] = parameters["Maxsets"]
                    # 세그먼트 생성
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

# 도표 상태로 루틴 출력
def output(routine):
    # 파일 이름 얻기
    filename = prompt.blurb("출력 파일의 이름을 지정할 항목을 선택하십시오(예: routine.xlsx)")
    if not ".xlsx" in filename:
        filename = filename + ".xlsx"
    # 도표 쓰기 시작
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    # 행 및 열 반복기 설정
    row = 0
    col = 0
    # 포맷 설정
    title = workbook.add_format({"bold": True, "align": "center", "font_color": "#ffffff", "bg_color": "#333333", "border": 1})
    dark = workbook.add_format({"align": "center", "font_color": "#ffffff", "bg_color": "#666666", "border": 1})
    gray = workbook.add_format({"align": "center", "bg_color": "#cccccc", "border": 1})
    light = workbook.add_format({"align": "center", "bg_color": "#eeeeee", "border": 1})
    white = workbook.add_format({"align": "center", "font_color": "#777777", "bg_color": "#ffffff", "border": 1})
    # 운동 포맷
    for exercise in routine:
        # strength,  HIIT 포맷
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
        # cardio 포맷
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