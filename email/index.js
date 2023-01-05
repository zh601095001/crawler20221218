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
            let {_id, isSendEmail, game_time, team_name1, team_name2, game_session, validity, total_score_1, total_score_2, leave_time} = records
            // 取第一个和最后一个
            const initialScore = records["start_score"]
            const currentScore = records["current_score"]
            // 计算分差
            let extremum = null // 当前值相对初始值情况
            if (initialScore && currentScore) {
                extremum = currentScore - initialScore
            }
            let type
            if (extremum) {
                type = extremum >= 0 ? "增量" : "减量"// 初始让分为正=>减量 负=>增量
            } else {
                type = null
            }
            validity = validity || 0.0
            return {
                _id, initialScore, currentScore, extremum, isSendEmail, game_time, team_name1, team_name2,
                game_session, validity, total_score_1, total_score_2, type, leave_time
            }
        })
        const finallyResults = targets
            // 阈值大于设定值
            .filter(target => {
                if (target.extremum && target.type === "增量") {
                    return Math.abs(target.extremum) >= process.env.INC_THRESHOLD
                } else if (target.extremum && target.type === "减量") {
                    return Math.abs(target.extremum) >= process.env.DES_THRESHOLD
                } else {
                    return false
                }
            })
            .filter(target => {
                return !target.isSendEmail
            })
        const displayResult = finallyResults.map(finallyResult => {
            const THRESHOLD_WITH_TYPE = finallyResult.type === "增量" ? process.env.INC_THRESHOLD : process.env.DES_THRESHOLD
            let initScoreTeamName = finallyResult.initialScore > 0 ? finallyResult.team_name1 : finallyResult.team_name2
            let currentScoreTeamName = finallyResult.currentScore > 0 ? finallyResult.team_name1 : finallyResult.team_name2
            const team_name_line3 = finallyResult.type === "减量" ? finallyResult.team_name1 : finallyResult.team_name2
            let signal
            if (finallyResult.initialScore > 0 && finallyResult.type === "减量" && finallyResult.currentScore >= 0) {
                signal = "-"
            } else if (finallyResult.initialScore < 0 && finallyResult.type === "增量" && finallyResult.currentScore <= 0) {
                signal = "-"
            } else {
                signal = "+"
            }
            return `
                    <h1>${finallyResult.game_time} ${finallyResult.game_session} [${finallyResult.leave_time}](${parseInt(finallyResult.validity) * 100}%)</h1>
                    <h1>${finallyResult.team_name1} ${finallyResult.total_score_1} | ${finallyResult.team_name2} ${finallyResult.total_score_2}</h1>
                    <h1>${team_name_line3}: ${signal}${Math.abs(finallyResult.currentScore)}</h1>
                    <div style="display: flex"><div style="font-weight: bold;">${currentScoreTeamName}当前让分值:</div><div>${finallyResult.currentScore}</div></div>
                    <div style="display: flex"><div style="font-weight: bold;">${initScoreTeamName}初始让分值:</div><div>${finallyResult.initialScore}</div></div>
                    <div style="display: flex"><div style="font-weight: bold;">${finallyResult.type}让分偏差:</div><div>${Math.abs(finallyResult.extremum)}</div></div>
                    <div style="display: flex"><div style="font-weight: bold;">${finallyResult.type}监控阈值:</div><div>${THRESHOLD_WITH_TYPE}</div></div>
                    <div style="display: flex"><div style="font-weight: bold;">触发时间:</div><div>${dayjs().format('YYYY-MM-DD HH:mm:ss')}</div></div>
                    <hr/>
            `
        }).join("")

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