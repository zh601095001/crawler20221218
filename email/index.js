require('dotenv').config({path: '.env'})
const {axios} = require("./axios")
const dayjs = require("dayjs")

;const {sendEmail} = require("./utils");
const {getSettings, getCreateTime} = require("./api");

setInterval(async () => {
    try {
        // 获取设置信息
        const settings = await getSettings()
        const basicSettings = settings.filter(setting => setting._id === "basicSettings")[0]
        const matchSettings = settings.filter(setting => !(setting._id === "basicSettings"))
        // 判断启动时间是否大于延迟监听时间
        const createTime = await getCreateTime()
        if (!((dayjs().unix() - createTime) / 60 / 60 >= basicSettings.delayTimeSpan)) {
            return
        }
        // 获取监控时间范围之内的比赛记录并计算让分差
        const {data} = await axios.post("/db/s",
            {createTime: {$gt: dayjs().unix() - basicSettings.monitorTimeSpan * 60 * 60}},
            {
                timeout: 1000 * 60 * 5
            }
        )
        const targets = data.data
            .filter(records => {
                const setting = settings.filter(item => {
                    if (!item.matchName) {
                        return false
                    }
                    // console.log(records["sclassName"][0])
                    return item.matchName.indexOf(records["sclassName"][0]) !== -1
                })[0]
                if (!setting) {
                    return false
                } else {
                    records["setting"] = setting
                    return true
                }
            })
            .map(records => {
                // 取第一个和最后一个
                let start_score
                if (records.setting.data.panName === "初盘") {
                    start_score = records["firstCount"] // 确定是终盘还是初盘，默认初盘
                } else {
                    start_score = records["lastCount"] // 确定是终盘还是初盘，默认初盘
                }
                records["start_score"] = start_score
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
                // 判断档位
                let level
                const inc_table = Object.entries(records.setting.data.inc_table)
                const inc_table_length = inc_table.length
                Object.entries(records.setting.data.inc_table).forEach(([index, item]) => {
                    index = parseInt(index)
                    if (index === 0 && start_score <= item.initialLetGoal[1]) {
                        level = 0
                    } else if (index === inc_table_length - 1 && start_score >= item.initialLetGoal[0]) {
                        level = index
                    } else if (start_score > item.initialLetGoal[0] && start_score <= item.initialLetGoal[1]) {
                        level = index
                    }
                })
                records["level"] = level
                return records
            })
        const finallyResults = targets
            // 阈值大于设定值
            .filter(target => {
                if (target.level === void 0) {
                    return false
                }
                if (target.extremum && target.type === "增量") {
                    const {threshold, Validity, isEffect} = target.setting.data.inc_table[`${target.level}`]
                    target["Validity"] = Validity
                    target["inc_threshold"] = threshold
                    target["isEffect"] = isEffect
                    console.log(target)
                    return Math.abs(target.extremum) >= threshold
                } else if (target.extremum && target.type === "减量") {
                    const {threshold, Validity, isEffect} = target.setting.data.des_table[`${target.level}`]
                    target["Validity"] = Validity
                    target["des_threshold"] = threshold
                    target["isEffect"] = isEffect
                    console.log(target)
                    return Math.abs(target.extremum) >= threshold
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
            const THRESHOLD_WITH_TYPE = finallyResult.type === "增量" ? finallyResult.inc_threshold : finallyResult.des_threshold
            let initScoreTeamName = finallyResult["start_score"] > 0 ? finallyResult["hometeam"][0] : finallyResult["guestteam"][0]
            let currentScoreTeamName = finallyResult["letGoal"] > 0 ? finallyResult["hometeam"][0] : finallyResult["guestteam"][0]
            let team_name_line3
            if (finallyResult.type === "减量") {
                if (!finallyResult.isEffect) {
                    team_name_line3 = finallyResult["guestteam"][0]
                } else {
                    team_name_line3 = finallyResult["hometeam"][0]
                }
            } else {
                if (!finallyResult.isEffect) {
                    team_name_line3 = finallyResult["hometeam"][0]
                } else {
                    team_name_line3 = finallyResult["guestteam"][0]
                }
            }
            let signal
            if (finallyResult["start_score"] > 0 && finallyResult.type === "减量" && finallyResult["letGoal"] >= 0) {
                signal = "-"
            } else if (finallyResult["start_score"] < 0 && finallyResult.type === "增量" && finallyResult["letGoal"] <= 0) {
                signal = "-"
            } else {
                signal = "+"
            }
            if (!finallyResult.isEffect) {
                if (signal === "+") {
                    signal = "-"
                }
                if (signal === "-") {
                    signal = "+"
                }
            }
            // 比赛状态修改
            let matchstate = finallyResult["matchstate"]
            const state = {};
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
                    <h1>${finallyResult["sclassName"][0]} (${finallyResult.Validity}) ${finallyResult.isEffect ? "<span style='color: #3ace23'>有效比赛</span>" : "<span style='color: red'>无效比赛</span>"}</h1>
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
            for (const email of basicSettings.receiveEmails) {
                await sendEmail({
                    to: email,
                    subject: "篮球实时数据通知",
                    content: displayResult,
                    ...basicSettings
                })
            }

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