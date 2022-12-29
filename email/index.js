require('dotenv').config({path: '.env'})
const {axios} = require("./axios")
const dayjs = require("dayjs")

;const {sendEmail} = require("./utils");

setInterval(async () => {
    try {
        // 判断启动时间是否大于延迟监听时间
        const responseTime = await axios.get("/db", {
            params: {
                collection: "time",
                _id: "lastRunTime"
            },
            timeout: 1000 * 60 * 5
        })
        const createTime = responseTime.data.data[0].createTime
        if (!((dayjs().unix() - createTime) / 60 / 60 >= process.env.DELAY_TIME_SPAN)) {
            return
        }
        // 获取监控时间范围之内的比赛记录并计算让分差
        const response = await axios.post("/db/s",
            {createTime: {$gt: dayjs().unix() - process.env.MONITOR_TIME_SPAN * 60 * 60}},
            {
                timeout: 1000 * 60 * 5
            }
        )
        const {data} = response.data
        const targets = data.map(records => {
            const {_id, isSendEmail, game_time, team_name1, team_name2, game_session} = records
            // 取第一个和最后一个
            const initialScore = records["start_score"]
            const currentScore = records["current_score"]
            // 计算分差
            let extremum = null // 当前值相对初始值情况
            if (initialScore) {
                extremum = currentScore - initialScore
            }
            return {
                _id, initialScore, currentScore, extremum, isSendEmail, game_time, team_name1, team_name2, game_session
            }
        })
        console.log(targets)
        const finallyResults = targets
            // 阈值大于设定值
            .filter(target => {
                if (target.extremum && target.extremum > 0) {
                    return Math.abs(target.extremum) >= process.env.INC_THRESHOLD
                } else if (target.extremum && target.extremum < 0) {
                    return Math.abs(target.extremum) >= process.env.DES_THRESHOLD
                } else {
                    return false
                }
            })
            // // 过滤初始值为正增加和初始值为负减少
            // .filter(target => {
            //     return !(target.initialScore > 0 && target.currentScore > target.initialScore ||
            //         target.initialScore < 0 && target.currentScore < target.initialScore
            //     )
            // })
            .filter(target => {
                return !target.isSendEmail
            })
        const displayResult = finallyResults.map(finallyResult => `
        <h1>${finallyResult.game_time} ${finallyResult.game_session}</h1>
        <h1>${finallyResult.team_name1} | ${finallyResult.team_name2}</h1>
        <div style="display: flex"><div style="font-weight: bold;">${finallyResult.currentScore > 0 ? finallyResult.team_name1 : finallyResult.team_name2}当前让分值:</div><div>${Math.abs(finallyResult.currentScore)}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">${finallyResult.initialScore > 0 ? finallyResult.team_name1 : finallyResult.team_name2}初始让分值:</div><div>${Math.abs(finallyResult.initialScore)}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">让分偏差:</div><div>${finallyResult.extremum}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">增量监控阈值:</div><div>${process.env.INC_THRESHOLD}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">减少监控阈值:</div><div>${process.env.DES_THRESHOLD}</div></div>
        <div style="display: flex"><div style="font-weight: bold;">触发时间:</div><div>${dayjs().format('YYYY-MM-DD HH:mm:ss')}</div></div>
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
            axios.put("/db", {
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