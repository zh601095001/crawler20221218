const {axios} = require("./axios");

const getSettings = async () => {
    return (await axios.get("/db", {
        params: {
            collection: "settings",
        },
        timeout: 1000 * 60 * 5
    })).data.data
}
const getCreateTime = async () => {
    const responseTime = await axios.get("/db", {
        params: {
            collection: "time",
            _id: "lastRunTime"
        },
        timeout: 1000 * 60 * 5
    })
    return responseTime.data.data[0].createTime
}
module.exports = {
    getSettings
}