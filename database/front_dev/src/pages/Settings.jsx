import React, {useContext, useEffect, useRef, useState} from 'react';
import {useGetSettingsMutation, useSetMatchSettingsMutation} from "../api/api";
import {Form, Input, Select, Table, Button, InputNumber} from 'antd';
import MatchsTables from "../components/MatchsTables";


function Settings() {
    const [getSettings, {isLoading}] = useGetSettingsMutation()
    const [setMatchSettings] = useSetMatchSettingsMutation()
    const [settings, setSettings] = useState(undefined)
    const [form] = Form.useForm()
    useEffect(() => {
        (async () => {
            const initSettings = await getSettings().unwrap()
            setSettings(initSettings)
        })()
    }, [getSettings])
    useEffect(() => {
        (async () => {
            const initSettings = await getSettings().unwrap()
            console.log(initSettings)
            const basicSettings = initSettings["data"].filter(item => item._id.startsWith("basicSettings"))[0]
            console.log(basicSettings)
            Object.entries(basicSettings).forEach(item => {
                form.setFieldValue(item[0], item[1])
            })
        })()
    }, [form, getSettings, settings])
    const handleApply = () => {
        form.submit()
    }
    const handleFinsh = (value) => {
        console.log(value)
        setMatchSettings({
            _id: "basicSettings",
            ...value
        })
    }
    if (isLoading) {
        return <div>加载中...</div>
    }
    if (settings) {
        const matchsId = settings["data"].filter(item => !item._id.startsWith("basicSettings")).map(item => item._id)
        return (
            <div>
                <div style={{fontWeight: "bold", fontSize: 16, display: "flex", justifyContent: "space-between"}}>
                    <div>基础设置</div>
                    <div><Button type="primary" onClick={handleApply}>应用</Button></div>
                </div>
                <hr style={{marginBottom: 5}}/>
                <Form
                    form={form}
                    labelCol={{
                        span: 4,
                    }}
                    wrapperCol={{
                        span: 14,
                    }}
                    onFinish={handleFinsh}
                >
                    <Form.Item label="邮件服务器" name="emailHost">
                        <Input/>
                    </Form.Item>
                    <Form.Item label="邮件端口" name="emailPort">
                        <InputNumber/>
                    </Form.Item>
                    <Form.Item label="邮箱账号" name="emailUser">
                        <Input/>
                    </Form.Item>
                    <Form.Item label="邮件密钥" name="emailPassword">
                        <Input.Password/>
                    </Form.Item>
                    <Form.Item label="延迟监控时间(h)" name="delayTimeSpan">
                        <InputNumber/>
                    </Form.Item>
                    <Form.Item label="监控时间范围(h)" name="monitorTimeSpan">
                        <InputNumber/>
                    </Form.Item>
                    <Form.Item label="历史数据抓取天数" name="historyCrawlerDay">
                        <InputNumber/>
                    </Form.Item>
                    <Form.Item label="邮件接收邮箱" name="receiveEmails">
                        <Select mode="tags" open={false}/>
                    </Form.Item>
                    <Form.Item label="代理订单API SecretId" name="secretId">
                        <Input/>
                    </Form.Item>
                    <Form.Item label="代理订单API SecretKey" name="secretKey">
                        <Input.Password/>
                    </Form.Item>
                    <Form.Item label="私密代理用户名" name="proxyUsername">
                        <Input/>
                    </Form.Item>
                    <Form.Item label="私密代理密码" name="proxyPassword">
                        <Input.Password/>
                    </Form.Item>
                    <Form.Item label="每次提取代理数" name="proxyNumber">
                        <InputNumber/>
                    </Form.Item>
                </Form>
                <div style={{fontWeight: "bold", fontSize: 16, marginTop: 10}}>联赛设置</div>
                <hr style={{marginBottom: 5}}/>
                {matchsId.map(_id => (<MatchsTables _id={_id}/>))}


            </div>
        );

    } else {
        return <div>error</div>
    }


}

export default Settings;