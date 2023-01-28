const data = require("./test.json")

Object.entries(data.data.inc_table).forEach(([k, v]) => {
    delete v.download_records
})
console.log(data.data.inc_table["0"].download_records)
