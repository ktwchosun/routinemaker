

from pyfiglet import Figlet
import routine
import prompt
import exercises
import xlsxwriter

@prompt.click.command()
def main() -> object:
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
        prompt.collect("어떤 유형을 선택1하시겠습니까?", exercises.unique(exercises.strength, "Variations"), equipment, lambda x: x + "s")
        pool = exercises.filter(exercises.strength, equipment, "Variations")
        # 무작위 또는 수동 운동 선택
        path = prompt.options("루틴에 맞는 운동을 어떻게 선택하시겠습니까?", ["랜덤 운동리스트 시작", "수동으로 운동 추가"])
        # 무작위로 연습 목록을 작성하기 시작
        if path == 1:
            # 관심있는 근육 그룹을 체크하고 후보자까지 범위를 좁히다
            muscles = []
            while len(muscles) < 1:
                prompt.collect("어떤 근육 그룹을 훈련시키고 싶나요?", exercises.unique(pool, "Group"), muscles)
                if len(muscles) < 1:
                    prompt.error("근육 그룹을 하나 이상 선택해야 합니다.")
            cart = routine.randomize(exercises.filter(pool, muscles, "Group"))
        # 수동으로 연습 추가
        elif path == 2:
            cart = routine.shop(pool)
        # add, remove, swap, or reorder exercises in cart
        cart = routine.edit(cart, pool)

    # 심장 박동 루틴 구성
    elif type == 2:
        # select activity
        activities = list(exercises.unique(exercises.cardio, "Group"))
        activity = activities[prompt.options("어떤 cardio 활동을 하고 싶으세요?", activities)-1]
        # get pool of exercises
        pool = exercises.filter(exercises.cardio, activity, "Group")
        # choose specific exercise
        if len(pool) > 1:
            cart = [pool[prompt.options("구체적으로 어떤 운동을 하고 싶으세요?", pool, key="Name")-1]]
        else:
            cart = [pool[0]]

    # HIIT 루틴 구성
    elif type == 3:
        # 무작위 또는 수동 운동 모집단 선택
        path = prompt.options("너의 루틴에 맞는 운동을 어떻게 선택하시겠습니까?", ["랜덤 운동리스트 시작", "수동으로 운동 추가"])
        # 무작위로 운동 목록을 작성하고 시
        if path == 1:
            cart = routine.randomize(exercises.HIIT)
        # 수동으로 연습 추가
        elif path == 2:
            cart = routine.shop(exercises.HIIT)
        # add, remove, swap, or reorder exercises in cart
        cart = routine.edit(cart, exercises.HIIT)

    # 파라미터 얻기
    parameters = routine.parameters(cart)

    # 루틴 발생
    data = routine.calculate(parameters)

    # 엑셀 스프레드시드로 루틴 출력
    routine.output(data)

if __name__ == '__main__':
    main()
