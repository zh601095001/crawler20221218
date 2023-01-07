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
        const {data} = await axios.post("/db/s",
            {createTime: {$gt: dayjs().unix() - process.env.MONITOR_TIME_SPAN * 60 * 60}},
            {
                timeout: 1000 * 60 * 5
            }
        )
        const targets = data.data.map(records => {
            // let {_id, isSendEmail,["matchtime,["hometeam,["guestteam,["matchstate, validity,["homescore, total_score_2,["remaintime} = records
            // 取第一个和最后一个
            const start_score = records["start_score"]
            const letGoal = records["letGoal"]
            // 计算分差
            let extremum = null // 当前值相对初始值情况
            if (start_score && letGoal) {
                extremum = letGoal - start_score
            }
            let type
            if (extremum) {
                type = extremum >= 0 ? "增量" : "减量"// 初始让分为正=>减量 负=>增量
            } else {
                type = null
            }
            records["extremum"] = extremum
            records["type"] = type
            records["validity"] = records["validity"] || 0.0
            return records
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
            .filter(target => {
                return !(!target["start_score"] || !target["letGoal"]);
            })
        const displayResult = finallyResults.map(finallyResult => {
            const THRESHOLD_WITH_TYPE = finallyResult.type === "增量" ? process.env.INC_THRESHOLD : process.env.DES_THRESHOLD
            let initScoreTeamName = finallyResult["start_score"] > 0 ? finallyResult["hometeam"][0] : finallyResult["guestteam"][0]
            let currentScoreTeamName = finallyResult["letGoal"] > 0 ? finallyResult["hometeam"][0] : finallyResult["guestteam"][0]
            const team_name_line3 = finallyResult.type === "减量" ? finallyResult["hometeam"][0] : finallyResult["guestteam"][0]
            let signal
            if (finallyResult["start_score"] > 0 && finallyResult.type === "减量" && finallyResult["letGoal"] >= 0) {
                signal = "-"
            } else if (finallyResult["start_score"] < 0 && finallyResult.type === "增量" && finallyResult["letGoal"] <= 0) {
                signal = "-"
            } else {
                signal = "+"
            }
            // 比赛状态修改
            let matchstate = finallyResult["matchstate"]
            const state = new Object();
            state[-5] = "推迟";
            state[-4] = "取消";
            state[-3] = "中断";
            state[-2] = "待定";
            state[-1] = "完";
            state[0] = "";
            state[1] = "1节";
            state[2] = "2节";
            state[3] = "3节";
            state[4] = "4节";
            state[5] = "1'OT";
            state[6] = "2'OT";
            state[7] = "3'OT";
            state["s-1"] = "上";
            state["s-3"] = "下";
            state[50] = "中场";
            finallyResult["matchstate"] = state[matchstate]
            return `
                    <h1>${finallyResult["sclassName"][0]} (${parseInt(finallyResult.validity) * 100}%)</h1>
                    <h1>${finallyResult["matchtime"].replace("<br>", " ")} ${finallyResult["matchstate"]} [${finallyResult["remaintime"]}]</h1>
                    <h1>${finallyResult["hometeam"][0]} vs ${finallyResult["guestteam"][0]} (${finallyResult["homescore"]}-${finallyResult["guestscore"]})</h1>
                    <h1>${team_name_line3}: ${signal}${Math.abs(finallyResult["letGoal"])}</h1>
                    <div style="display: flex"><div style="font-weight: bold;">${currentScoreTeamName}当前让分值:</div><div>${finallyResult["letGoal"]}</div></div>
                    <div style="display: flex"><div style="font-weight: bold;">${initScoreTeamName}初始让分值:</div><div>${finallyResult["start_score"]}</div></div>
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