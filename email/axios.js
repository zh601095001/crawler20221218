const axios = require("axios")

axios.defaults.baseURL = process.env.BASE_URL

module.exports = {
    axios
}