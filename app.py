import re
import pandas as pd
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def add_space_to_korean_words(text):
    pattern = re.compile(r'(?<![ㄱ-ㅎㅏ-ㅣ가-힣])((?!도|시|군|구|읍|면|로|길)[ㄱ-ㅎㅏ-ㅣ가-힣]+)')
    result = re.sub(pattern, r' \1', text)
    return result

def add_space_to_uppercase_letters(text):
    pattern = re.compile(r'(?<=[a-zA-Z\d가-힣])(?=[A-Z])')
    result = re.sub(pattern, ' ', text)
    return result

def add_space_to_numbers(text):
    pattern = re.compile(r'(?<!-)(?<!\d)(\d+)')
    result = re.sub(pattern, r' \1', text)
    return result

def remove_commas(text):
    result = text.replace(',', '')
    return result

def convert_hybrid_words(text):
    # 정규표현식을 사용하여 한영혼용단어를 찾습니다.
    pattern1 = r'([가-힣]+)-do'
    pattern2 = r'([가-힣]+)-si'
    pattern3 = r'([가-힣]+)-gu'
    pattern4 = r'([가-힣]+)-gun'
    pattern5 = r'([가-힣0-9]+)-ro'
    pattern6 = r'([가-힣0-9]+)-gil'
    
    pattern7 = r'([a-zA-Z]+)도'
    pattern8 = r'([a-zA-Z]+)시'
    pattern9 = r'([a-zA-Z]+)구'
    pattern10 = r'([a-zA-Z]+)군'
    pattern11 = r'([a-zA-Z]+)로'
    pattern12 = r'([a-zA-Z]+)길'
    
    matches1 = re.findall(pattern1, text)
    matches2 = re.findall(pattern2, text)
    matches3 = re.findall(pattern3, text)
    matches4 = re.findall(pattern4, text)
    matches5 = re.findall(pattern5, text)
    matches6 = re.findall(pattern6, text)
    matches7 = re.findall(pattern7, text)
    matches8 = re.findall(pattern8, text)
    matches9 = re.findall(pattern9, text)
    matches10 = re.findall(pattern10, text)
    matches11 = re.findall(pattern11, text)
    matches12 = re.findall(pattern12, text)
    
    for match in matches1:
        converted_word = match + '도'
        text = text.replace(match + '-do', converted_word)
    for match in matches2:
        converted_word = match + '시'
        text = text.replace(match + '-si', converted_word)
    for match in matches3:
        converted_word = match + '구'
        text = text.replace(match + '-gu', converted_word)
    for match in matches4:
        converted_word = match + '군'
        text = text.replace(match + '-gun', converted_word)
    for match in matches5:
        converted_word = match + '로'
        text = text.replace(match + '-ro', converted_word)
    for match in matches6:
        converted_word = match + '길'
        text = text.replace(match + '-gil', converted_word)
    for match in matches7:
        converted_word = match + '-do'
        text = text.replace(match + '도', converted_word)
    for match in matches8:
        converted_word = match + '-si'
        text = text.replace(match + '시', converted_word)
    for match in matches9:
        converted_word = match + '-gu'
        text = text.replace(match + '구', converted_word)
    for match in matches10:
        converted_word = match + '-gun'
        text = text.replace(match + '군', converted_word)
    for match in matches11:
        converted_word = match + '-ro'
        text = text.replace(match + '로', converted_word)
    for match in matches12:
        converted_word = match + '-gil'
        text = text.replace(match + '길', converted_word)
    
    return text

# Load data from the other Excel file (contains the mapping)
mapping_file = 'data.xlsx'
mapping_df = pd.read_excel(mapping_file)

# Create a dictionary mapping English words to Korean words
mapping_dict = dict(zip(mapping_df['로마자표기'], mapping_df['한글']))

# 함수 내 영어 단어를 한글로 변환하는 부분
def replace_english_with_korean(sentence):
    def replace_word(match):
        word = match.group(0)
        return mapping_dict.get(word, word)

    return re.sub(r'\b[A-Za-z-]+\b', replace_word, sentence)

def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = list(range(len(s1) + 1))
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min(distances[index1], distances[index1 + 1], new_distances[-1]))
        distances = new_distances

    return distances[-1]

def correct_typo(input_word, valid_words):
    min_distance = float('inf')
    corrected_word = None

    for word in valid_words:
        distance = levenshtein_distance(input_word, word)
        if distance < min_distance:
            min_distance = distance
            corrected_word = word

    return corrected_word

def correct_and_translate(input_word, valid_words, mapping_dict):
    corrected_word = correct_typo(input_word, valid_words)
    translated_word = mapping_dict.get(corrected_word, corrected_word)
    return translated_word


# Load mapping data from the Excel file
mapping_file = 'data.xlsx'
mapping_df = pd.read_excel(mapping_file)
mapping_dict = dict(zip(mapping_df['로마자표기'], mapping_df['한글']))

def perform_address_search(search_data):
    api_key = 'devU01TX0FVVEgyMDIzMDcyODE1MzkzNzExMzk3MzA='
    base_url = 'http://www.juso.go.kr/addrlink/addrLinkApi.do'

    payload = {
        'confmKey': api_key,
        'currentPage': '1',
        'countPerPage': '10',
        'resultType': 'json',
        'keyword': search_data,
    }

    response = requests.get(base_url, params=payload)

    if response.status_code == 200:
        search_result = response.json()
        if 'results' in search_result and 'juso' in search_result['results']:
            result_data = search_result['results']['juso']
            if result_data:
                return [result.get('roadAddr', '') for result in result_data]

    return ['F']

@app.route('/search', methods=['POST'])
def search():
    try:
        if request.is_json:
            request_data = request.get_json()
            request_list = request_data.get('requestList', [])
            results = []

            for req in request_list:
                seq = req.get('seq')
                address = req.get('requestAddress')

                formatted_address = address
                formatted_address = add_space_to_korean_words(formatted_address)
                formatted_address = add_space_to_uppercase_letters(formatted_address)
                formatted_address = add_space_to_numbers(formatted_address)
                formatted_address = remove_commas(formatted_address)
                

                pattern1 = r"\b[\w-]*-do\b|\b[\w-]*도\b"
                pattern2 = r"\b[\w-]*-si\b|\b[\w-]*시\b|\bSeoul\b|\b서울\b|\bBusan\b|\b부산\b|\bGwangju\b|\b광주\b|\bDaegu\b|\b대구\b|\bDaejeon\b|\b대전\b|\bUlsan\b|\b울산\b|\bIncheon\b|\b인천\b"
                pattern3 = r"\b[\w-]*-gu\b|\b[\w-]*구\b|\b[\w-]*gu\b"
                pattern4 = r"\b[\w-]*-gun\b|\b[\w-]*군\b"
                pattern5 = r"\b[\w-]*-eup\b|\b[\w-]*읍\b"
                pattern6 = r"\b[\w-]*-myeon\b|\b[\w-]*(?<!으)면\b"
                pattern7 = r"\b[\w-]*로\b|\b[\w-]*-daero\b|\b[\w-]*-ro\b|\b\w+\s*Station-ro\b|\b\w+\s*Ring-ro\b"
                pattern8 = r"\b[\w-]*-gil\b|\b[\w-]*길\b"
                pattern9 = r"(?<!\S)(G|B|GF|BF|G/F|underground|B/F|지하|(?<=\s)B(?=\,))(?!\S)" 
                pattern10 = r"(?<!\S)(\d+(?:-\d+)?)(?!\S)"

                processed_data = [
                    [formatted_address],
                ]
                
                for address_row in processed_data:
                    result = ""
                    address = ' '.join(address_row)

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
                        result += match1.group(0) + " "
                    if match2:
                        result += match2.group(0) + " "
                    if match3:
                        result += match3.group(0) + " "
                    if match4:
                        result += match4.group(0) + " "
                    if match5:
                        result += match5.group(0) + " "
                    if match6:
                        result += match6.group(0) + " "
                    if match7:
                        result += match7.group(0) + " "
                    if match8:
                        result += match8.group(0) + " "
                    if match9:
                        result += re.sub(pattern9, '지하', match9.group(0)) + " "
                    if match10:
                        result += match10.group(0) + " "

                    result = convert_hybrid_words(result.strip())
                    result = replace_english_with_korean(result.strip())  # 영어 단어 한글 변환 적용
                    result = correct_and_translate(result.strip(), mapping_df['로마자표기'], mapping_dict)  # 오타 수정 및 번역 적용
                    results.append(result)

                response_data = {'HEADER': {'RESULT_CODE': 'S', 'RESULT_MSG': 'Success'}, 'BODY': results}
                return jsonify(response_data)
        else:
            response_data = {'HEADER': {'RESULT_CODE': 'F', 'RESULT_MSG': 'Invalid JSON data'}}
            return jsonify(response_data)
    except Exception as e:
        response_data = {'HEADER': {'RESULT_CODE': 'F', 'RESULT_MSG': str(e)}}
        return jsonify(response_data)
