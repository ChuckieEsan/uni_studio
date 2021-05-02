let msgOK = (s) => {
    Toastify({
        text: s,
        duration: 3000,
        backgroundColor: "linear-gradient(to right, #00b09b, #00b09b)",
    }).showToast();
}
let msgFail = (s) => {
    Toastify({
        text: s,
        duration: 3000,
        backgroundColor: "linear-gradient(to right, #EF100F, #EF100F)",
    }).showToast();
}
$(document).ready(function () {
    console.log(123)
    //Check to see if the window is top if not then display button
    $(window).scroll(function () {
        let st = $(this).scrollTop()
        if (st > 100 && st<document.body.scrollHeight-$(window).height()) {
            $('.scrollTo').fadeIn();

        } else {
            $('.scrollTo').fadeOut();
        }
    });

    //Click event to scroll to top
    $('.toTop').click(function () {
        $('html, body').animate({
            scrollTop: 0
        }, 800);
        return false;
    });
    $('.toBottom').click(function () {
        $('html, body').animate({
            scrollTop: document.body.scrollHeight
        }, 800);
        return false;
    });
});