const axios = require("axios")
const dayjs = require("dayjs");

const baseURL = process.env.BASE_URL || "http://localhost:8000"
const recordsURL = process.env.CRAWLER_RECORDS || "http://localhost:6000"
const getSettings = async () => {
    return (await axios.get(baseURL + "/db", {
        params: {
            collection: "settings",
        },
        timeout: 1000 * 60 * 5
    })).data.data
}
const getMatchSettings = async () => {
    return (await axios.get(baseURL + "/db", {
        params: {
            collection: "settings",
        },
        timeout: 1000 * 60 * 5
    })).data.data.filter(setting => !(setting._id === "basicSettings")).map(item => item.data)
}
const getCreateTime = async () => {
    const responseTime = await axios.get(baseURL + "/db", {
        params: {
            collection: "time",
            _id: "lastRunTime"
        },
        timeout: 1000 * 60 * 5
    })
    return responseTime.data.data[0].createTime
}
const getMatches = async (monitorTimeSpan) => {
    const {data} = await axios.post(baseURL + "/db/s",
        {createTime: {$gt: dayjs().unix() - monitorTimeSpan * 60 * 60}},
        {
            timeout: 1000 * 60 * 5
        }
    )
    return data.data
}
const changeState = async (_id) => {
    await axios.put(baseURL + "/db", {
        _id,
        isSendEmail: true
    }, {
        timeout: 1000 * 60 * 5
    })
}
const getRecords = async ({_id, sep_time = 12, isEffect = 1}) => {
    const {data, status} = await axios.get(recordsURL + "/records", {
        params: {
            _id,
            sep_time,
            isEffect
        }
    })
    return {data, status}
}

const addEmail = async (data) => {
    const res = await axios.post(baseURL + "/db", data, {
        params: {
            collection: "email"
        }
    })
    return res.status
}
module.exports = {
    getSettings,
    getMatchSettings,
    getCreateTime,
    getMatches,
    getRecords,
    changeState,
    addEmail
}