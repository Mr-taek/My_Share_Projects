# 사용법
1. mein.py 를 실행시키면 pos 창이 나옵니다
2. 새로 추가하고 싶은 메뉴가 있다면 menu.json에 작성된 양식을 따라서 작성하면 됩니다
3. 새로운 재료가 추가되었을 경우 stock.json 


- .exe만들기 prompt 와 스탭
1. pyinstaller --onedir --noconsole --clean --optimize=2 --name=MyApp main.py

  --onefile : 모든 의존성을 하나의 실행 파일로 묶음 → 배포가 간단해짐.

  --noconsole : 콘솔 창을 숨김 (GUI 앱일 경우 필수).

  --clean : 빌드 과정에서 불필요한 캐시/임시 파일 제거 → 실행 파일 크기 최소화.

  --optimize=2 : 바이트코드 최적화 → 실행 속도 향상.

  --name=MyApp : 생성될 실행 파일 이름 지정.

2. .exe만든 후 escpos 라이브러리를 복사해서 _internal 에 복붙하기

3. MyAPP 폴더에 아래 파일 넣기
  1. [text](systemInfo.json)
  2. [text](menu.json)
  3. [text](dist/MyApp/stock.json)

main.py : 변환할 파이썬 스크립트.

- 특징
  1. dist/MyApp/ 폴더가 생성되고, 그 안에 MyApp.exe와 필요한 모든 라이브러리(.dll, .pyd, .pyc 등)가 함께 들어갑니다.

  2. 실행 시 압축 해제 과정이 없으므로 시작 속도가 빠릅니다.

  3. 누락된 라이브러리를 직접 확인할 수 있고, 필요하면 추가 파일을 수동으로 넣을 수도 있습니다.
    + .exe 파일로 만들경우 escpos가 계속 누락됨으로 직접 site-packages에 넣어야 실행시 에러가 발생하지 않습니다