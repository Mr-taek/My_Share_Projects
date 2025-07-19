from cnocr import CnOcr
import pinyin as pin
"""
https://github.com/breezedeus/cnocr : cnocr 출처, 및 예제

사진은 가급적 딱 한 줄, 그림판 픽셀은 25x25 맞춰서 넘겨야 함. 막 500,100 만큼 크면 모델이 인식 자체를 못해서 "빈 리스트"를 넘겨버림.

이 라이브러리 같은 경우 자주 오류가 생겨서, 이 프로그램을 만든 컴퓨터의 라이브러리에 수정본이 있음

필요시 요청바람
"""
ocr = CnOcr()
res = ocr.ocr(fr'kbs2.jpg')
for ele in res:
    sounds=pin.get(ele["text"],delimiter=" ")
    print(ele)
    print(f"발음 : {sounds}")