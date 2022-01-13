/*
* 필요한 함수 선언
*/
// 카테고리 콤보박스(<select>)의 <option> 태그 정보 (text, value) 가져오기
function getCategory() {
    select = document.getElementsByClassName("W110 MgT1")[0];
    options = select.getElementsByTagName("option");
    option_list = []
    for (i = 0; i < options.length; i++) {
        option = options[i];
        option_list.push({
            "text": option.text,
            "value": option.getAttribute("value")
        });
    }
    return option_list;
}

// 비동기 delay
function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// 카테고리 선택 후 조회 함수 호출 후 테이블 크롤링
async function fnSearchInfo(category_info, arr_result, delay_ms) {
    value = category_info.value;
    $("select[id='mang_code']").val(value).prop("selected", true);
    searchInfo2();
    await sleep(delay_ms);
    
    console.log("test");
    table = document.getElementsByTagName("table")[0];
    tbody = table.getElementsByTagName("tbody")[0]; 
    tr_list = tbody.getElementsByTagName("tr");
    
    for (i = 0; i < tr_list.length; i++) {
        tr = tr_list[i];
        th = tr.getElementsByTagName("th")[0];
        id = th.getAttribute("id");
        a_tags = tr.getElementsByTagName("a");
        name = a_tags[0].text;
        addr = a_tags[1].text;
    }
}

// 호출 함수
async function fnProcess(arr_category, arr_result, delay_ms) {
    await arr_category.reduce((prevTask, currTask) => {
        return prevTask.then(() => fnSearchInfo(currTask, arr_result, delay_ms));
    }, Promise.resolve());
    
    console.log('Finished');
}

console.log('Start');
/*
* Step.1 카테고리 정보 가져오기
*/
caterories = getCategory();

/*
* Step.2 전체 카테고리 조회
*/
arr_result = []
fnProcess(caterories, arr_result, 1000);
