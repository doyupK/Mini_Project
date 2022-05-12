//해당 지역 시 목록
function get_locations() {

    let do_name = window.location.href
    let do_num = do_name.substring(do_name.length - 1, do_name.length)

    $.ajax({
        type: "GET",
        url: "/city_lists",
        data: {"do": do_num},
        success: function (response) {
            $('.cards-area').eq(0).empty()
            let rows = response
            rows.forEach((data, i) => {
                //UI 메서드
                draw_tabs(data, i)
                document.getElementsByClassName("select-location")[i].addEventListener('click', tab_event)
            })
        },
        complete: function () {

            document.getElementsByClassName("select-location")[0].click()
            // let first = document.getElementsByClassName("select-location")[0].innerHTML
            // console.log(first)
            // get_select_data(first, 0)

            if (!!sessionStorage.getItem("active")) {
                let mapId = sessionStorage.getItem("active")

                $("#"+mapId).css("fill", "cadetblue").css("stroke", "aquamarine");
            }

        }
    });
}

function tab_event() {

    let area = this.innerText
    let allEl = document.getElementsByClassName("select-location")
    let tabIdx = Array.from(allEl).indexOf(this)
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
        },
        complete: function () {
            let cards = document.getElementsByClassName('card');
            [...cards].forEach((card, idx) => {
                card.addEventListener('click', (e) => {
                    let title = document.getElementsByClassName('beach-title')[idx].innerHTML
                    let code = document.getElementsByClassName('beach_code')[idx].innerHTML
                    let lat = document.getElementsByClassName("lat")[idx].innerHTML
                    let lng = document.getElementsByClassName("lng")[idx].innerHTML
                    window.location.href = "/locations/detail/"+title+"/"+code+"/"+lat+"/"+lng
                })
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
    let {name,code, lat, lng} = data
    let card = ` <div class="col">
                        <div class="card h-100 w-100">
                            <img src="../static/img/sample.jpg" class="card-img-top" alt="...">
                            <div class="card-body">
                                <h5 class="card-title"><b class ="beach-title">${name}</b></h5>
                                <p class="card-text"></p>
                                 <span class = 'beach_code' style="display: none">${code}</span>
                                <span class = 'lat' style="display: none">${lat}</span>
                                <span class = 'lng' style="display: none">${lng}</span>
                            </div>
                        </div>
                    </div>`

    $('.cards-area').eq(i).append(card)
}


get_locations()