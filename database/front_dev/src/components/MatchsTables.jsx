import React, {useEffect, useState} from 'react';
import temp from "../data.json";
import MatchsTable from "./MatchsTable";
import {useDeleteMatchSettingsMutation, useGetMatchSettingsMutation, useSetMatchSettingsMutation} from "../api/api";
import {Button} from "antd";

function MatchsTables({_id}) {
    const [getMatchSettings, {isFetching}] = useGetMatchSettingsMutation()
    const [setMatchSettings] = useSetMatchSettingsMutation()
    const [deleteMatchSettings] = useDeleteMatchSettingsMutation()
    const [dataSource, setDataSource] = useState({})
    const handleDataChange = (newDataSource) => {
        setDataSource(newDataSource)
        setMatchSettings({
            _id,
            data: newDataSource
        })
    }
    const handleDelete = async () => {
        try {
            await deleteMatchSettings({_id}).unwrap()
            window.location.reload()
        } catch (e) {
            console.log(e)
            window.location.reload()
        }

    }
    useEffect(() => {
        (async () => {
            const settings = await getMatchSettings({_id}).unwrap()
            if (settings["data"].length > 0) {
                const data = JSON.parse(JSON.stringify(settings["data"][0]["data"]))
                setDataSource(data)
            }
        })()
    }, [_id, getMatchSettings])
    if (!Object.getOwnPropertyNames(dataSource).length) {
        return <div>加载中...</div>
    }
    console.log(dataSource)
    return (
        <div>
            <div style={{fontSize: 20, fontWeight: "bold"}}>监控联赛：{_id}&nbsp;<Button type="danger" onClick={handleDelete}>删除</Button></div>
            <div>&nbsp;{dataSource.panName} | 阈值范围：{dataSource.thresholdRange.join("~")} | 触发率：{(dataSource.reachRate * 100).toFixed(2)}% | 统计比赛总数：{dataSource.totalCount}</div>
            <MatchsTable type={1} dataSource={dataSource} onDataChange={handleDataChange}/>
            <MatchsTable type={2} dataSource={dataSource} onDataChange={handleDataChange}/>
        </div>
    );
}

export default MatchsTables;