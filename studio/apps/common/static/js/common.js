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