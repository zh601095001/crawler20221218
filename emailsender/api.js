const {axios} = require("./axios");
const baseURL = process.env.BASE_URL || "http://localhost:8000"
const getSettings = async () => {
    return (await axios.get(baseURL + "/db", {
        params: {
            collection: "settings",
        },
        timeout: 1000 * 60 * 5
    })).data.data.filter(setting => setting._id === "basicSettings")[0]
}
const getEmails = async (status) => {
    return (await axios.post(baseURL + "/db/s", {"status": status}, {
        params: {
            collection: "email",
        }
    })).data.data
}
const changeEmailState = async ({_id, status = 3}) => {
    return (await axios.put(baseURL + "/db", {_id, status}, {
        params: {
            collection: "email",
        }
    }))
}

module.exports = {
    getEmails,
    getSettings,
    changeEmailState
}