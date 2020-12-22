let check = () => {
    $("#source").removeAttr("disabled")
    if ($("#content").val() == '') {
        $("#messages").text("不可为空！")
        $("#source").attr("disabled", "disabled")
        $("#submit").attr("disabled", "disabled")
        $("#submit").text("请等待")
        setTimeout(() => {
            $("#submit").removeAttr("disabled")
            $("#submit").text("提交")
        }, 1000)
        return false;
    }
    return true;
}

let hangon = ()=>{
    $("#submit").attr("disabled", "disabled")
    $("#submit").text("请等待")
    setTimeout(() => {
        $("#submit").removeAttr("disabled")
        $("#submit").text("提交")
    }, 1500)
}