(function () {
    $.getScript("/NBA/sbOdds.js?t=" + Date.parse(new Date()))
    return JSON.stringify(sData)
})
()