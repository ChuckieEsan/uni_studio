let refreshRules = () => {
    fetch(RULES_URL).then(res => res.json()).then(res => {
        res.map((v, i) => {
            let BADGE_HTML = `<span id="rules_${i}" 
                class="badge badge-warning"style="float:right;
                margin-top:13px;margin-right: 10px;">
            ${v}&nbsp;&nbsp;<a id="${v}" onclick="deleteRules('${v}')" href="#">&times;</a>
        </span>`
            $("#rules").html($("#rules").html() + BADGE_HTML)

        })
        let ADD_HTML = `<span id="add_rule" 
                class="badge badge-warning"style="float:right;
                margin-top:13px;margin-right: 10px;">
                <input type="text" id="ruleInput" style="display:none">
            <a id="addRule" href="#">
                +
            </a>
        </span>`

        $("#rules").html($("#rules").html() + ADD_HTML)
        $("#addRule").click(() => {
            if ($("#addRule").text().indexOf('+') != -1) {
                $("#addRule").text('√')
                $("#ruleInput").show()
            } else {
                let rule = $("#ruleInput").prop('value')
                if (!rule) {
                    refreshRules()
                    return
                }
                fetch(`${RULES_URL}?rule=${$("#ruleInput").prop('value')}`, {
                    method: "POST"
                }).then(res => {
                    $("#rules").html('')
                    refreshRules()
                }).catch(err => {
                    console.log(err)
                    msgFail("网络错误")
                })
            }
        })
    }).catch(err => {
        console.log(err)
        msgFail("网络错误")
    })
}
let deleteRules = (ruleString) => {
    fetch(`${RULES_URL}?rule=${ruleString}`, {
        method: "DELETE",
    }).then((res) => {
        $("#rules").html('')
        refreshRules()
    }).catch(err => {
        console.log(err)
        msgFail("网络错误")
    })
}
$(document).ready(function () {
    refreshRules()
})