import json

import requests


def get_main_list():
    results = list()
    base_code = list()

    with open('./static/location_data.json', 'r', encoding="UTF-8") as base:
        json_data = json.load(base)
        base_code = json_data["code"]['all']

    cnt = 0
    for base in base_code:
        params = {
            "ServiceKey": "nB8EIND5cjQ8UsOhFLrjFg==",
            "BeachCode": base,
            "ResultType": json

        }
        response = requests.get(
            "http://www.khoa.go.kr/api/oceangrid/beach/search.do", params=params)
        print(response.json().get("result"))
        cnt = cnt + 1
        if cnt > 8: break


if __name__ == "__main__":
    get_main_list()
