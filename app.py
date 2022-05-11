import hashlib
from django.core.paginator import Paginator
from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import jwt as jwt
import googlemaps
import data_resource
from get_data import get_locations, get_list_by_location

gmap = data_resource.gmap

ca = certifi.where()

client = data_resource.client
db = client.dbsparta
app = Flask(__name__)


hash_key = data_resource.SECRET_KEY

@app.route('/')
def intro():
    return render_template('intro.html')


@app.route('/home')
def home():
    token_receive = request.cookies.get('mytoken')

    if token_receive is not None:
        payload = jwt.decode(token_receive, hash_key, algorithms=['HS256'])
        user_info = db.fin_users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('index.html', user_info=user_info,
                               login_status=login_status)
    else:
        login_status = 0
        return render_template('index.html', login_status=login_status)


# 도 하위 시별 리스트
@app.route('/city_lists')
def locations():
    select_do = request.args.get("do")
    return jsonify(get_locations(select_do))


# 도에 해당 하는 지역 리스트 반환
@app.route('/find_by_city')
def find_by_city():
    received_city = request.args.get("city")
    return jsonify(get_list_by_location(received_city))


# fin 게시글 저장 - 220509 DY
@app.route('/surfer/write_post', methods=['POST'])
def save_posts():
    token_receive = request.cookies.get('mytoken')

    payload = jwt.decode(token_receive, hash_key, algorithms=['HS256'])
    user_info = db.fin_users.find_one({"id": payload["id"]})

    review_list = list(db.fin_Reviews.find({}, {'_id': False}))

    if len(review_list) == 0:
        count = 1
    else:
        last_post_no = review_list[-1]['post_num']
        count = int(last_post_no) + 1

    location_receive = request.form['location_give']
    name_receive = request.form['name_give']
    # 주소 -> 위/경도 변환
    result = gmap.geocode(name_receive)
    n_lat = result[0]['geometry']['location']['lat']
    n_lng = result[0]['geometry']['location']['lng']
    content_receive = request.form['content_give']

    file = request.files["file_give"]
    # 확장자명 만듬
    extension = file.filename.split('.')[-1]

    # datetime 클래스로 현재 날짜와시간 만들어줌 -> 현재 시각을 출력하는 now() 메서드
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'
    # 파일에 시간붙여서 static폴더에 filename 으로 저장
    save_to = f'static/img/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'post_num': count,
        'username': user_info["id"],
        'profile_name': user_info["name"],
        'location': location_receive,
        'spot_name': name_receive,
        'content': content_receive,
        'lat': n_lat,
        'lng': n_lng,
        'file': f'{filename}.{extension}',
        'time': today.strftime('%Y.%m.%d'),
        'COMMENT': []
    }

    db.fin_Reviews.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


# 회원 가입 by 220509 DY
@app.route("/users_signup", methods=["POST"])
def users():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    keyword_receive = request.form['keyword_give']

    # Encrypt
    pw_encode = pw_receive.encode()
    pw_hash = hashlib.sha256(pw_encode).hexdigest()

    doc = {
        'id': id_receive,
        'pw': pw_hash,
        'name': name_receive,
        'keyword': keyword_receive
    }
    db.fin_users.insert_one(doc)

    return jsonify({'msg': '회원 가입 완료!'})


# 아이디 중복 확인 220510 DY
@app.route("/users_idCheck", methods=["GET"])
def getId():
    id_receive = request.values.get('id_give')
    user = db.fin_users.find_one({'id': id_receive})
    if user is None:  # datatype 이 none일경우 []를 통한 접근 불가 ex) user is None <- ok but, user['id'] is None <- 데이터 타입 오류
        return jsonify({'user': True})
    else:
        return jsonify({'user': False})


# 로그인 220510 DY
@app.route('/sign_in', methods=['POST'])
def sign_in():
    id_receive = request.form['give_id']
    pw_receive = request.form['give_pw']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')
                             ).hexdigest()  # 패스워드 암호화

    result = db.fin_users.find_one(
        {'id': id_receive, 'pw': pw_hash})  # 동일한 유저가 있는지 확인

    if result is not None:  # 동일한 유저가 없는게 아니면, = 동일한 유저가 있으면,
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, hash_key,
                           algorithm='HS256')  # .decode('utf8')
        # .decode('utf8')  # 토큰을 건내줌.
        return jsonify({'result': 'success', 'token': token, 'msg': '환영합니다.'})
    else:  # 동일한 유저가 없으면,
        return jsonify({'result': 'fail', 'msg': '아이디/패스워드가 일치하지 않습니다.'})


#  Recommend 페이지 - 220509 DY
@app.route('/FIN_list')
def fin_listpage():
    token_receive = request.cookies.get('mytoken')
    posts_list = list(db.fin_Reviews.find({}, {'_id': False}).sort('post_num', -1))
    page = request.args.get('page', type=int, default=1)
    paginator = Paginator(posts_list, 8)
    posts = paginator.page(page)

    page_numbers_range = 10  # 페이지 메뉴에 표현 될 페이지 수 제한
    max_index = paginator.num_pages  # 전체 페이지 수
    current_page = int(page) if page else 1  # 현재 페이지 / 기본값 1
    start_index = int((current_page - 1) / page_numbers_range) * \
                  page_numbers_range  # 페이지 메뉴의 시작 번호
    end_index = start_index + page_numbers_range  # 페이지 메뉴의 끝 번호

    if end_index >= max_index:
        end_index = max_index
    page_numbers_range = paginator.page_range[start_index:end_index]

    if token_receive is not None:
        payload = jwt.decode(token_receive, hash_key, algorithms=['HS256'])
        user_info = db.fin_users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('recommend_list.html', user_info=user_info, login_status=login_status, posts=posts,
                               page_numbers_range=page_numbers_range)
    else:
        login_status = 0
        return render_template('recommend_list.html', login_status=login_status, posts=posts,
                               page_numbers_range=page_numbers_range)


# Recommend 상세페이지 by DY
@app.route('/detail/<keyword>')
def detail(keyword):
    # 로그인 정보 불러오기
    find_keyword = int(keyword)
    token_receive = request.cookies.get('mytoken')
    # 코멘트 불러오기
    comments_name = db.fin_Reviews.find_one({'post_num': find_keyword}, {
        'COMMENT': 1, '_id': False})
    # 해당(keyword) 게시물 정보 불러오기
    review = db.fin_Reviews.find_one({'post_num': find_keyword})
    # 로그인 정보(token)있을 시
    if token_receive is not None:
        payload = jwt.decode(token_receive, hash_key, algorithms=['HS256'])
        user_info = db.fin_users.find_one({"id": payload["id"]})
        login_status = 1
        if len(comments_name) == 0:
            return render_template('recommend_detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('recommend_detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)
    # 로그인 정보(token)없을 시
    else:
        user_info = None
        login_status = 0
        if len(comments_name) == 0:
            return render_template('recommend_detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('recommend_detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)


# 코멘트 저장 220429 DY
@app.route('/saveComment', methods=['POST'])
def save_comment():
    global comments
    pageInfo_receive = request.form['pageInfo_give']
    postNum_receive = int(request.form['postNum_give'])
    userName_receive = request.form['userName_give']
    comment_receive = request.form['comment_give']

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, hash_key, algorithms=['HS256'])
    user_info = db.fin_users.find_one({"id": payload["id"]})
    if pageInfo_receive == "fin":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.fin_Reviews.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})

    if len(comments['COMMENT']) == 0:
        doc = {
            'comment_id': 1,
            'userID': user_info['id'],
            'username': userName_receive,
            'comment': comment_receive
        }
    else:
        list_comment = list(comments['COMMENT'])
        last_comment = list_comment[-1]
        new_comment_id = int(last_comment.get('comment_id')) + 1

        doc = {
            'comment_id': new_comment_id,
            'userID': user_info['id'],
            'username': userName_receive,
            'comment': comment_receive
        }
    if pageInfo_receive == "fin":
        db.fin_Reviews.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})

    return jsonify({'msg': '저장 완료!'})


# Detail Page Comment 삭제 by DY
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    pageInfo_receive = request.form['pageInfo_give']
    postNum_receive = int(request.form['postNum_give'])
    commentNum_receive = int(request.form['commentNum_give'])

    # post Number 찾아서 해당 게시글 DB 정보에서 삭제
    if pageInfo_receive == "fin":
        db.fin_Reviews.update_many({'post_num': postNum_receive},
                               {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})

    return jsonify({'msg': '삭제 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
