function getTable() {
    table = document.getElementsByTagName("table")[0];
    tbody = table.getElementsByTagName("tbody")[0]; 
    tr_list = tbody.getElementsByTagName("tr");

    result = [];
    for (i = 0; i < tr_list.length; i++) {
        tr = tr_list[i];
        th = tr.getElementsByTagName("th")[0];
        id = th.getAttribute("id");
        a_tags = tr.getElementsByTagName("a");
        name = a_tags[0].text;
        addr = a_tags[1].text;
        result.push({'id': id, 'name': name, 'addr': addr});
    }
    
    return result;
}

getTable();