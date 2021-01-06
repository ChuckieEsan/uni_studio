
let toggleCheckedStyle = (loopid) => {
    if ($(`#label_${loopid}`).hasClass('check-btn-checked')) {
        $(`#label_${loopid}`).removeClass('check-btn-checked')
        //$(`#label_${loopid}`).addClass('check-btn')
    } else {
        $(`#label_${loopid}`).addClass('check-btn-checked')
        //$(`#label_${loopid}`).removeClass('check-btn')
    }
}
let showDesc = (loopid) => {
    $("#diaryText").text($(`#Desc_long_${loopid}`).text())
    $("#diaryModal").modal('show')
}
$("#submitVote").click((e)=>{
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
    console.log(cptinput)
    if (!cptinput) {
        msgFail("验证码不可为空")
        return
    }
    let form = $("#voteForm")
    let formData = form.serialize()
    $("#submitVote").attr("disabled","disabled")
    $("#submitVote").text("请等待")
    fetch(SUBMIT_URL,{
        method:"POST",
        headers:{
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body:formData,
        redirect:"follow"
    }).then(res=>{
        if(res.redirected){
            location.href = res.url
        }
        setTimeout(()=>{$("#submitVote").removeAttr("disabled");$("#submitVote").text('提交')},1500)
        return res.json()
    }).then(res=>{
        if(!res.success){
            msgFail(res.details)
            $("#captchaImg").attr("src",$("#captchaImg").attr("src")+`?t=${new Date().getTime()}`)
        }
    }).catch((err)=>{
        console.log(err)
        msgFail("网络错误")
    })
})
function getLocalTime(nS) {     
    return new Date(parseInt(nS) * 1000).toLocaleString().replace(/:\d{1,2}$/,' ');     
}
var myChart = echarts.init(document.getElementById('timeline'));
myChart.showLoading();
fetch(STATS_URL).then(res => res.json()).then(res => {
    console.log(res)
    let legends = Object.keys(res)
    let data = {}
    for(let i=0;i<legends.length;i++){
        data[legends[i]] = []
        let now = 1607601600//1607601600//1607601600//12.10 20:00
        let step = 900//15min
        let end = Date.parse(new Date())/1000;//1607601600 + 48*3600//1608135600//1607659200//1608135600//12.16 24:00 
        let max = 0
        let timeArr = Object.keys(res[legends[i]])
        //console.log(res[legends[i]])
        //console.log(timeArr)
        while(now<=end){
            
            if(parseInt(timeArr[0])>=now){//最新的时间比当前时间大，直接推0
                data[legends[i]].push(max)
                now = now + step
                continue
            } else {
                let t=0;
                while(parseInt(timeArr[t])<now && t!=timeArr.length-1){
                    t++;
                }
                max = res[legends[i]][timeArr[t]]
                data[legends[i]].push(max) 
                now = now + step
                continue
            } 
        }
        //console.log(data[legends[i]])
        //console.log('-------')
        //break
    }
    let result = []
    Object.keys(data).map((v,i)=>{
        result[i] = {
            name:v,
            type:'line',
            data:data[v]
        }
    })
    let ta = []
    let now = 1607601600//1607601600//1607601600//12.10 20:00
    let step = 900//15min
    let end = Date.parse(new Date())/1000;//1607601600 + 48*3600//1608135600//1607659200//1608135600//12.16 24:00 
    for(let i=0;i<(end-now)/step;i++){
        let ts = 1607601600 + i*900
        ta.push(getLocalTime(ts))
    }
    //console.log('ta:',ta)
    //console.log('result:',result)
    let option = {
        title: {
            text: '排行榜--时间顺序'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: legends
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            data: ta
        },
        yAxis: {
            type: 'value',
            name: '票数',
            min:0,
            max:1000,
            interval:20
        },
        series: result
    };
    // specify chart configuration item and data
    console.log(option.legend)

    // use configuration item and data specified to show chart
    myChart.setOption(option);
    myChart.hideLoading();
})
