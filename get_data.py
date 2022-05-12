import json
from functools import lru_cache

import requests

with open('./static/location_data.json', 'r', encoding="UTF-8") as base:
    json_data = json.load(base)

with open('./static/beach_info.json', 'r', encoding="UTF-8") as f:
    json_beach_data = json.load(f)


@lru_cache
def get_locations(do=0):
    countries = list()
    location = json_data["locations"]
    countries = json_data["do"][location[do]]
    return countries


# 시명 기준 으로 데이터 가져오기
@lru_cache
def get_list_by_location(city):
    location_code = json_data['code'][city]
    return find_by_code_to_json(location_code)


# json 파일에서 코드명으로 해수욕장 이름 , 위경도 데이터 가져오기
def find_by_code_to_json(codes):
    result = list()
    for code in codes:
        result.append(json_beach_data[code])
    return result


# 해당 도 하위 시 데이터 모두 가져오기
@lru_cache
def get_main_list(do="강원"):
    results_main = list()
    base_code = list()

    countries = json_data["do"][do]
    for country in countries:
        codes = json_data["code"][country]
        base_code += codes

    results = find_by_code(base_code)

    return results


# 해변 코드로 기상 정보 가져오기
def find_by_code(location_code):
    results = list()
    for code in location_code:
        params = {
            "ServiceKey": "nB8EIND5cjQ8UsOhFLrjFg==",
            "BeachCode": code,
            "ResultType": json

        }
        response = requests.get(
            "http://www.khoa.go.kr/api/oceangrid/beach/search.do", params=params)
        json_respo = response.json().get("result")
        beach_name = json_respo.get('meta').get('beach_name')
        base_info = json_respo.get("data")[0]

        if 'wind_speed' in base_info and 'water_temp' in base_info:
            base_info['beach'] = beach_name
            results.append(base_info)

    return results


if __name__ == "__main__":
    get_list_by_location("양양")
