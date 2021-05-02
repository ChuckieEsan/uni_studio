$(function () {
    $("img.lazy").lazyload({
        threshold: 200
    });
});
let toggleCheckedStyle = (loopid) => {
    if ($(`#label_${loopid}`).hasClass('check-btn-checked')) {
        $(`#label_${loopid}`).removeClass('check-btn-checked')
        //$(`#label_${loopid}`).addClass('check-btn')
    } else {
        $(`#label_${loopid}`).addClass('check-btn-checked')
        //$(`#label_${loopid}`).removeClass('check-btn')
    }
}
$("#submitVote").click((e) => {
    e.preventDefault()
    let minVote = VOTE_MIN
    let maxVote = VOTE_MAX
    let count = $("input[name='candidates']:checked").length;
    console.log(count)
    if (count < minVote || count > maxVote) {
        msgFail(`最少${minVote}票，最多${maxVote}票，已投${count}票`)
        return
    }
    let cptinput = $("#captchaInput").val()
    if (!cptinput) {
        msgFail("验证码不可为空")
        return
    }
    let form = $("#voteForm")
    let formData = form.serialize()
    $("#submitVote").attr("disabled", "disabled")
    $("#submitVote").text("请等待")
    fetch(SUBMIT_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData,
        redirect: "follow"
    }).then(res => {
        if (res.redirected) {
            location.href = res.url
        }
        setTimeout(() => {
            $("#submitVote").removeAttr("disabled");
            $("#submitVote").text('提交')
        }, 1500)
        return res.json()
    }).then(res => {
        if (!res.success) {
            msgFail(res.details)
            $("#captchaImg").attr("src", $("#captchaImg").attr("src") +
                `?t=${new Date().getTime()}`)
        }
    }).catch((err) => {
        console.log(err)
        msgFail("网络错误")
    })
})