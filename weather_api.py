import math
from datetime import date, datetime, timedelta

import requests

import data_resource
from api_exception import ApiException, CheckErr

service_key = data_resource.weather_key


# 반환 값
# opt 0: today, today_date, base_date, base_time
# opt 1: base_time(현재 시간 기준 최신 갱신 시간)
# opt 2: all_time(현재 시간 기준 회신 갱신 시간 포함 이전 시간)
def get_current_base_time(opt=1):
    # 오늘
    today = datetime.today()  # 현재 지역 날짜 반환
    today_date = today.strftime("%Y%m%d")  # 오늘의 날짜 (연도/월/일 반환)

    # 어제
    yesterday = date.today() - timedelta(days=1)
    yesterday_date = yesterday.strftime('%Y%m%d')

    now = datetime.now()
    hour = now.hour
    minute = now.minute
    base_time = ""

    update_time = "0200 0500 0800 1100 1400 1700 2000 2300".split()

    base_date = today_date
    if (hour < 2) and (minute <= 10):
        today_date = yesterday_date
        base_time = update_time.pop()
    cnt = 1
    for idx, time in enumerate(update_time):
        if (cnt < hour) and (hour < (cnt + 4)):
            base_time = update_time[idx]

            break
        else:
            cnt += 3

    if opt == 0:
        return today, today_date, base_date, base_time
    else:
        return base_time


# 온도,습도,강수량,습도,풍속 데이터
# 현재 시간 데이터 요청
def get_weather_info(lat=38.005, lng=128.731):
    page_no = '1'
    num_of_rows = '12'
    data_type = 'JSON'

    nx, ny = grid(lat, lng)
    today, today_date, base_date, base_time = get_current_base_time(0)

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

    params = {
        'serviceKey': service_key,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        'dataType': data_type,
        'base_date': today_date,
        'base_time': base_time,
        'nx': nx, 'ny': ny
    }
    try:
        response = requests.get(url, params=params)

        state_code = response.json().get('response').get('header').get('resultCode')
        CheckErr(state_code)
    except ApiException as e:
        print(e)

    return weather_filter_info(response, base_time, 0)


# 현재 시간 기준 5시간분 데이터
def until_current_time_info(lat=38.005, lng=128.731):
    page_no = '1'
    num_of_rows = '72'
    data_type = 'JSON'
    today_date = datetime.today().strftime("%Y%m%d")
    nx, ny = grid(lat, lng)
    base_time = get_current_base_time(1)

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

    params = {
        'serviceKey': service_key,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        'dataType': data_type,
        'base_date': today_date,
        'base_time': base_time,
        'nx': nx, 'ny': ny
    }
    try:
        response = requests.get(url, params=params)
        state_code = response.json().get('response').get('header').get('resultCode')
        CheckErr(state_code)
    except ApiException as e:
        print(e)
    return weather_filter_info(response, base_time, 1)


# 날씨 정보 데이터 필터링 및 반환, 0: 현재시간 데이터, 1: 5시간 이내 예측 데이터
def weather_filter_info(response, base_time, opt):
    today = datetime.now()
    datas = response.json().get('response').get('body').get('items')
    data = dict()

    base = today.strftime('%Y-%m-%d')
    data['date'] = base
    weather_data = dict()

    fcst_time = str(int(base_time) + 100)
    all_time_data = list()

    for item in datas['item']:

        category = item['category']
        if opt == 1:
            # 시간에 따른 기상 데이터 리스트 append
            if not fcst_time == item['fcstTime']:
                fcst_time = item['fcstTime']
                all_time_data.append(weather_data)
                weather_data = {}

        # 1 시간 기온 코드
        if category == 'TMP':
            weather_data["fcstTime"] = item['fcstTime']
            weather_data['tmp'] = item['fcstValue']


        # 일 최고 기온
        elif category == 'TMX':
            weather_data['tmx'] = item['fcstValue']

        # 일 최저 기온
        elif category == 'TMN':
            weather_data['tmn'] = item['fcstValue']

        # 풍속(동서)
        elif category == 'UUU':
            weather_data['uuu'] = item['fcstValue']

        # 풍속(남북)
        elif category == 'VVV':
            weather_data['vvv'] = item['fcstValue']

        # 파고
        elif category == 'WAV':
            weather_data['wav'] = item['fcstValue']

        # 풍향
        elif category == 'VEC':
            weather_data['vec'] = item['fcstValue']

        # 풍속 코드
        elif category == 'WSD':
            weather_data['wsd'] = item['fcstValue']

        # 강수 확률
        elif category == 'POP':
            weather_data['pop'] = item['fcstValue']

        # 하늘 상태 코드
        elif category == 'SKY':
            sky_code = item['fcstValue']
            if sky_code == '1':
                weather_data['sky'] = '맑음'
            elif sky_code == '3':
                weather_data['sky'] = '구름 많음'
            elif sky_code == '4':
                weather_data['sky'] = '흐림'

        # 기상 상태
        elif category == 'PTY':
            weather_code = item['fcstValue']

            if weather_code == '1':
                weather_state = '비'
            elif weather_code == '2':
                weather_state = '비/눈'
            elif weather_code == '3':
                weather_state = '눈'
            elif weather_code == '5':
                weather_state = '빗방울'
            elif weather_code == '6':
                weather_state = '빗방울 눈날림'
            elif weather_code == '7':
                weather_state = '눈날림'
            else:
                weather_state = False
            weather_data['state'] = weather_state
    if opt == 0:
        data['weather'] = weather_data
    else:
        data['weather'] = all_time_data
    return data


# 위도 경도 , 기상청 x,y 좌표로 변경
def grid(lat, lng):
    v1, v2 = float(lat), float(lng)
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기1준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    rs = {}

    ra = math.tan(math.pi * 0.25 + v1 * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)

    theta = v2 * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    rs['x'] = math.floor(ra * math.sin(theta) + XO + 0.5)
    rs['y'] = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    str_x = str(rs["x"]).split('.')[0]
    str_y = str(rs["y"]).split('.')[0]

    return str_x, str_y


if __name__ == "__main__":
    print(get_weather_info())
    print(until_current_time_info())
