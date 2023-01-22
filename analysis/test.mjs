import fetch from "node-fetch";
fetch("http://localhost:5000/matches?dateRange=1640995200000,1672531200000", {
    "headers": {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "Pycharm-4a3d9d43=ea17fa13-dd72-4fa8-82a4-55f70b0acc42; _ga=GA1.1.1316778226.1674036457; _ga_79RNL76N7N=GS1.1.1674036456.1.1.1674036586.0.0.0",
        "Referer": "http://localhost:8000/",
        "Referrer-Policy": "strict-origin-when-cross-origi n"
    },
    "body": null,
    "method": "GET"
}).catch(e => {
    console.log(e)
})