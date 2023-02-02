const axios = require("axios")

axios.defaults.baseURL = process.env.BASE_URL || "http://localhost:8000"

module.exports = {
    axios
}