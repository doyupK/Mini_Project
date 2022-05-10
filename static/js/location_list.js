//해당 지역 시 목록
function get_locations() {

    let do_name = window.location.href
    let do_num = do_name.substring(do_name.length - 1, do_name.length)
    $.ajax({
        type: "GET",
        url: "/city_lists",
        data: {"do": do_num},
        success: function (response) {
            let rows = response
            rows.forEach((data, i) => {
                //UI 메서드
                draw_tabs(data, i)

                document.getElementsByClassName("select-location")[i].addEventListener('click', tab_event)
            })
        },
        complete: function () {
            document.getElementsByClassName("select-location")[0].classList.add("active")
            $('.tab-pane').eq(0).show()
            let first = document.getElementsByClassName("select-location")[0].innerHTML
            console.log(first)
            get_select_data(first, 0)

        }
    });
}

function tab_event() {

    let area = this.innerText
    let allEl = document.getElementsByClassName("select-location")
    let tabIdx = Array.from(allEl).indexOf(this)
    console.log(tabIdx)
    $('.cards-area').eq(tabIdx).empty()
    get_select_data(area, tabIdx)

}

//수온, 풍속, 풍향 데이터
function get_select_data(area, tabIdx) {
    let location = area
    console.log(tabIdx)
    $.ajax({
        type: "GET",
        url: "/find_by_city",
        data: {"city": area},
        success: function (response) {
            let rows = response
            console.log(response)
            rows.forEach((data) => {
                //UI 메서드
                draw_cards(data, tabIdx)
            })
        }
    });
}

//tab 생성, tab content 생성
function draw_tabs(locations, i) {
    let nav = `<li class="nav-item">
                    <a class="nav-link select-location" data-bs-toggle="tab" href="#box${i}">${locations}</a>
                </li>`

    let nav_content = `<div class="tab-pane container" id="box${i}" style="width: 55vw">
                            <div class="row row-cols-1 row-cols-md-4 g-4 cards-area">
                            </div>
                        </div>`


    $('#box-tabs').append(nav)
    $('#box-contents').append(nav_content)


}


// UI 생성 tab content, cards
// param('filtering location forecast data')
function draw_cards(data, i) {
    let {beach, wind_speed, water_temp, wind_direct, obs_time} = data
    let card = ` <div class="col">
                        <div class="card h-100">
                            <img src="../static/img/sample.jpg" class="card-img-top" alt="...">
                            <div class="card-body">
                                <h5 class="card-title"><b>${beach}</b></h5>
                                <p class="card-text"></p>
                                <p class="card-text">현재 수온: &nbsp;${water_temp}C°&nbsp;</p>
                                <p class="card-text">현재 풍속: &nbsp;${wind_speed}m/s&nbsp;</p>
                                <p class="card-text">현재 풍향: &nbsp;${wind_direct}&nbsp;</p>
                                <sub>공개 출처: 해양 수산부</sub>
                            </div>
                        </div>
                    </div>`

    $('.cards-area').eq(i).append(card)
}


get_locations()