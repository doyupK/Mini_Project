// 회원 가입 기능 =================================================================================

var checkIdResult = false
var checkIdDuplicationResult = false
var checkPasswordResult = false
var checkPasswordConfirmResult = false
var checkNameResult = false
var checkKeywordResult = false

// 아이디 조합 체크
function checkId(id) { // 아이디 입력값 검증
    checkIdDuplicationResult = false
    var regex = new RegExp(/^[A-Za-z0-9]{4,12}$/); // 4~12자리 영문,숫자 조합 정규 표현식 활용
    var element = document.getElementById('checkIdResult');
    if (regex.exec(id)) {
        element.innerHTML = '사용 가능';
        element.style.color = 'green';
        checkIdResult = true; // 전역변수값을 true 로 변경
    } else {
        element.innerHTML = '사용 불가능';
        element.style.color = 'red';
        checkIdResult = false; // 전역변수값을 false 로 변경
    }
}

// 비밀번호 조합 체크
function checkPassword(password) {
    var lengthRegex = /^[A-Za-z0-9!@#$%]{8,16}$/;
    var engUpperCaseRegex = /[A-Z]/;
    var engLowerCaseRegex = /[a-z]/;
    var digitRegex = /[0-9]/;
    var specRegex = /[!@#$%]/;
    var element = document.getElementById('checkPasswordResult');
    if (lengthRegex.exec(password)) {
        var safetyCount = 0;
        if (engUpperCaseRegex.exec(password)) safetyCount++;
        if (engLowerCaseRegex.exec(password)) safetyCount++;
        if (digitRegex.exec(password)) safetyCount++;
        if (specRegex.exec(password)) safetyCount++;

        switch (safetyCount) {
            case 4:
                element.innerHTML = '매우 안전';
                element.style.color = 'green';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 3:
                element.innerHTML = '안전';
                element.style.color = 'yellow';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 2:
                element.innerHTML = '보통';
                element.style.color = 'orange';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 1:
                element.innerHTML = '사용불가';
                element.style.color = 'red';
                checkPasswordResult = false; // 전역변수값을 false 로 변경
                break;
        }
    } else {
        element.innerHTML = '영문자,숫자,특수문자 초쇠 2가지 조합 필수!';
        element.style.color = 'red';
        checkPasswordResult = false; // 전역변수값을 false 로 변경
    }
}

function checkPasswordConfirm(password) { // 패스워드 일치 확인
    var element = document.getElementById('passwordConfirmResult');
    if (password == $('#floatingInput_PW').val()) { // 패스워드 확인 내용 일치 시
        element.innerHTML = '패스워드 일치';
        element.style.color = 'green';
        checkPasswordConfirmResult = true; // 전역변수값을 true 로 변경
    } else {
        element.innerHTML = '패스워드 불일치';
        element.style.color = 'red';
        checkPasswordConfirmResult = false; // 전역변수값을 false 로 변경
    }
}

// 회원 가입
function users_signUp() {
    let id = $('#floatingInput_ID').val()
    let password = $('#floatingInput_PW').val()
    let name = $('#floatingInput_name').val()
    let keyword = $('#floatingInput_keyword').val()

    if (name != '') {
        checkNameResult = true
    }
    if (keyword != '') {
        checkKeywordResult = true
    }

    switch (false) {
        case checkIdResult:
            alert('아이디를 확인하세요');
            return;
        case checkIdDuplicationResult:
            alert('아이디 중복확인 필수 입니다');
            return;
        case checkPasswordResult:
            alert('비밀번호를 확인하세요');
            return;
        case checkPasswordConfirmResult:
            alert('비밀번호가 일치하지 않습니다');
            return;
        case checkNameResult:
            alert('이름을 입력하세요');
            return;
        case checkKeywordResult:
            alert('이메일을 입력하세요');
            return;
        default:
            $.ajax({
                type: 'POST',
                url: '/users_signup',
                data: {
                    id_give: id,
                    pw_give: password,
                    name_give: name,
                    keyword_give: keyword
                },
                success: function (response) {
                    alert(response['msg'])
                    window.location.href = "/"
                }
            });
    }
}

// 아이디 중복체크
function users_idCheck() {
    let id = $('#floatingInput_ID').val()
    $.ajax({
        type: "GET",
        url: "/users_idCheck",
        data: {id_give: id},
        success: function (response) {
            if (response['user']) {
                checkIdDuplicationResult = true
                alert("사용가능한 아이디 입니다.")
            } else {
                checkIdDuplicationResult = false
                alert("사용할수 없습니다.")
            }
        }
    })
}





// 김민수 : 회원 가입 및 관리 기능 =================================================================================

