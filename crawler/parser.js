(function (table_id) {
    const obj = {}
    // 获取比赛时间
    obj["game_time"] = document.evaluate(`//*[@id='table_${table_id}']/tbody/tr[1]/td[1]/text()[1]`, document, null, 2).stringValue
    obj["team_name"] = document.getElementById(`team_${table_id}`).innerHTML
    obj["team_name2"] = document.getElementById(`team2_${table_id}`).innerHTML
    obj["game_session"] = document.getElementById(`zt_${table_id}`).innerHTML
    const hl = document.getElementById(`hl_${table_id}`).innerHTML.match(/^<span class="odds2.*?">(.*?)<\/span>.*?$/)
    const gl = document.getElementById(`gl_${table_id}`).innerHTML.match(/^<span class="odds2.*?">(.*?)<\/span>.*?$/)
    let current_score = null
    if (hl) {
        current_score = hl[1]
    }
    if (gl) {
        current_score = gl[1]
    }
    obj["current_score"] = current_score

    return JSON.stringify(obj)
})
("id_xxx")