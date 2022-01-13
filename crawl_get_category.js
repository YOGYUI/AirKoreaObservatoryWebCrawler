// 카테고리 콤보박스(<select>)의 <option> 태그 정보 (text,     ) 가져오기
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

getCategory();