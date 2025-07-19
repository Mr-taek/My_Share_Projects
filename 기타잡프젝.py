def progress_bar():
    """
    진행바를 출력하는 함수
    """
    # 진행바의 개수와 문자 설정

    진행바개수 = 10 # 이 값을 조절하면 진행도 를 조절할 수 있다
    진행중="☆" # ㅁ + 한자 키를 누르면 7번에 있는 문자이다
    진행완료="★" # ㅁ + 한자 키를 누르면 8번에 있는 문자이다
    for i in range(진행바개수+1): # +1 을 해준 건 진행바는 총 10 개인데 range 특성상 10-1 인 9까지만 출력하기 때문이다.
        inPrograss=진행중*(진행바개수-i) # ☆ * (10-3) = ☆ * 7
        finishProgress=진행완료*i # ★ * 3 
        if i==진행바개수:
            print(finishProgress+inPrograss+ " 완료 !!",end="\n")
        else:
            print(finishProgress+inPrograss,end="\r") # \r 을 응용하면 이러한 것도 만들 수 있게 된다\
            
        for _ in range(10000000): # 단순 프로그램 시간끌기용 for문 , 0이 7개다
            pass