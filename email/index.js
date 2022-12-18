require('dotenv').config({path: '.env'})
const axios = require("axios")
const dayjs = require("dayjs")

;const {sendEmail} = require("./utils");

setInterval(async () => {
    try {
        const responseTime = await axios.get("http://localhost:8000/db", {
            params: {
                collection: "time",
                _id: "lastRunTime"
            },
            timeout: 1000 * 60 * 5
        })
        const createTime = responseTime.data.data[0].createTime
        // 判断启动时间是否大于延迟监听时间
        if (!((dayjs().unix() - createTime) / 60 / 60 >= process.env.DELAY_TIME_SPAN)) {
            return
        }
        const response = await axios.post("http://localhost:8000/db/s",
            {createTime: {$gt: dayjs().unix() - process.env.MONITOR_TIME_SPAN * 60 * 60}},
            {
                timeout: 1000 * 60 * 5
            }
        )
        const {data} = response.data
        const targets = data.map(records => {
            const _id = records._id
            const {isSendEmail} = records
            // 取第一个和最后一个
            const initialScore = records["start"]["score"]
            const currentScore = records["end"]["score"]
            const extremum = initialScore - currentScore
            return {
                _id, initialScore, currentScore, extremum, isSendEmail
            }
        })
        // console.log(targets)
        const finallyResults = targets
            // 阈值大于设定值
            .filter(target => {
                return Math.abs(target.extremum) >= process.env.THRESHOLD
            })
            // 过滤初始值为正增加和初始值为负减少
            .filter(target => {
                return !(target.initialScore > 0 && target.currentScore > target.initialScore ||
                    target.initialScore < 0 && target.currentScore < target.initialScore
                )
            })
            .filter(target => {
                return !target.isSendEmail
            })
        const displayResult = finallyResults.map(finallyResult => `
        <h1>${finallyResult._id}</h1>
        <div style="display: flex"><div style="font-weight: bold;">${finallyResult.initialScore > 0 ? "主队" : "客队"}初始让分值:</div><div>${Math.abs(finallyResult.initialScore)}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">${finallyResult.currentScore > 0 ? "主队" : "客队"}当前让分值:</div><div>${Math.abs(finallyResult.currentScore)}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">让分偏差:</div><div>${finallyResult.extremum}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">触发条件:</div><div>${process.env.THRESHOLD}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">触发时间:</div><div>${dayjs().format("MMM D, YYYY h:mm A")}</div></div>
        <hr/>
    `).join("")

        if (finallyResults.length) {
            await sendEmail({
                to: process.env.RECEIVE_EMAIL || process.env.EMAIL_USER,
                subject: "篮球实时数据通知",
                content: displayResult
            })
            await sendEmail({
                to: "601095001@qq.com",
                subject: "篮球实时数据通知",
                content: displayResult
            })
            console.log(finallyResults)
        }
        finallyResults.forEach(result => {
            axios.put("http://localhost:8000/db", {
                _id: result._id,
                isSendEmail: true
            }, {
                timeout: 1000 * 60 * 5
            })
        })

    } catch (e) {
        console.log(e)
    }
}, 3000)

