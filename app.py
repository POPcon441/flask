import re

url = "http://127.0.0.1:9999/search"

data = {
    "requestList": [
          {"seq": "000001", "requestAddress": "28, Namcheon-dong-ro 19beon-gil, Suyeong-gu, Busan, Suyeong Tax Office Building파란건물"},
          {"seq": "000002", "requestAddress": "Seoul Gangnam Police Station, 11, Teheran-ro 114-gil, Gangnam-gu, Seoul, please keep at office"},
          {"seq": "000003", "requestAddress": "Dobong Tax Office, 117, Dobong-ro, Gangbuk-gu, Seoul문 앞"},
          {"seq": "000004", "requestAddress": "Gwanak Police Station, 33, Gwanak-ro 5-gil, Gwanak-gu, Seoul직접수령"},
          {"seq": "000005", "requestAddress": "Dongdaemun Police Station, 29, Yaknyeongsi-ro 21-gil, Dongdaemun-gu, Seoul문서수발실"},
    ]
}
def translate_address(request_address):
    # 주소를 영문에서 한글로 변환하는 로직을 구현하세요.
    # 이 예시에서는 단순히 영문 주소를 그대로 반환합니다.
    return request_address

def remove_bom(text):
    # BOM 제거하는 함수
    return text.lstrip('\ufeff')

def add_space_to_korean_words(text):
    # 한글 단어 앞에 공백 추가하는 함수
    pattern = re.compile(r'(?<![ㄱ-ㅎㅏ-ㅣ가-힣])((?!도|시|군|구|읍|면|로|길)[ㄱ-ㅎㅏ-ㅣ가-힣]+)')
    result = re.sub(pattern, r' \1', text)
    return result

def add_space_to_uppercase_letters(text):
    # 영어 대문자 앞에 공백 추가하는 함수
    pattern = re.compile(r'(?<=[a-zA-Z\d])(?=[A-Z])')
    result = re.sub(pattern, ' ', text)
    return result

def add_space_to_numbers(text):
    # 숫자 앞에 공백 추가하는 함수
    pattern = re.compile(r'(?<!-)(?<!\d)(\d+)')
    result = re.sub(pattern, r' \1', text)
    return result

def remove_commas(text):
    # ',' 삭제하는 함수
    result = text.replace(',', '')
    return result

responseList = []

for item in data["requestList"]:
    seq = item.get('seq')
    request_address = item.get('requestAddress')
    result_address = translate_address(request_address)
    result_address = remove_bom(result_address)
    result_address = add_space_to_korean_words(result_address)
    result_address = add_space_to_uppercase_letters(result_address)
    result_address = add_space_to_numbers(result_address)
    result_address = remove_commas(result_address)
    responseList.append({'seq': seq, 'resultAddress': result_address})

# 패턴 정의
pattern1 = r"\b[\w-]*-do\b|\b[\w-]*도\b"
pattern2 = r"\b[\w-]*-si\b|\b[\w-]*시\b|\bSeoul\b|\b서울\b|\bBusan\b|\b부산\b|\bGwangju\b|\b광주\b|\bDaegu\b|\b대구\b|\bDaejeon\b|\b대전\b|\bUlsan\b|\b울산\b|\bIncheon\b|\b인천\b"
pattern3 = r"\b[\w-]*-gu\b|\b[\w-]*구\b|\b[\w-]*gu\b"
pattern4 = r"\b[\w-]*-gun\b|\b[\w-]*군\b"
pattern5 = r"\b[\w-]*-eup\b|\b[\w-]*읍\b"
pattern6 = r"\b[\w-]*-myeon\b|\b[\w-]*(?<!으)면\b"
pattern7 = r"\b[\w-]*로\b|\b[\w-]*-daero\b|\b[\w-]*-ro\b"
pattern8 = r"\b[\w-]*-gil\b|\b[\w-]*길\b"
pattern9 = r"(?<!\S)(G|B|GF|BF|G/F|underground|B/F|지하|(?<=\s)B(?=\,))(?!\S)"
pattern10 = r"(?<!\S)(\d+(?:-\d+)?)(?!\S)"

# 패턴 적용 및 결과 저장
results = []

for item in responseList:
    seq = item.get('seq')
    address = item.get('resultAddress')

    result = []  # 새로운 주소 변환을 시작할 때마다 result 리스트 초기화

    match1 = re.search(pattern1, address)
    match2 = re.search(pattern2, address)
    match3 = re.search(pattern3, address)
    match4 = re.search(pattern4, address)
    match5 = re.search(pattern5, address)
    match6 = re.search(pattern6, address)
    match7 = re.search(pattern7, address)
    match8 = re.search(pattern8, address)
    match9 = re.search(pattern9, address)
    match10 = re.search(pattern10, address)

    if match1:
        result.append(match1.group(0) + " ")
    if match2:
        result.append(match2.group(0) + " ")
    if match3:
        result.append(match3.group(0) + " ")
    if match4:
        result.append(match4.group(0) + " ")
    if match5:
        result.append(match5.group(0) + " ")
    if match6:
        result.append(match6.group(0) + " ")
    if match7:
        result.append(match7.group(0) + " ")
    if match8:
        result.append(match8.group(0) + " ")
    if match9:
        result.append(re.sub(pattern9, '지하', match9.group(0)) + " ")
    if match10:
        result.append(match10.group(0) + " ")

    results.append({'seq': seq, 'resultAddress': ''.join(result).strip()})

for result in results:
    print(result)

