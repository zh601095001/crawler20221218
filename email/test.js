const {axios} = require("./axios")
;(async () => {
    const res = await axios.get("http://localhost:8000/db",{
            params: {
                collection: "time",
                _id: "lastRunTime"
            },
            timeout: 1000 * 60 * 5
        })
    console.log(res)
})()
