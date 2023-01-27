import React, {useEffect, useState} from 'react';
import {Select, Form, Button, InputNumber, Table, Modal, DatePicker} from "antd";
import styles from "../styles/home.module.less"
import {Column} from "@ant-design/charts";
import {useAnalysisMatchedMutation, useGetAllMatchNamesMutation, useSetEmailMutation} from "../api/api";
// import data from "../data.json"
// todo:临时测试
// import matchNames from "../matchs.json"

const {Option} = Select

// matchNames = Object.entries(matchNames)
const {RangePicker} = DatePicker

function Home() {
    const [form] = Form.useForm()
    const [dateForm] = Form.useForm()
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [chartData, setChartData] = useState([])
    const [data, setData] = useState({}) // 分析结果
    const [matchNames, setMatchNames] = useState([])
    const [getAllMatchNames, {isLoading}] = useGetAllMatchNamesMutation()
    const [analysis, {isLoading: isAnalysis}] = useAnalysisMatchedMutation()
    const [setEmail, {isLoading: isSetEmail}] = useSetEmailMutation()
    useEffect(() => {
        form.setFieldValue(["range", "min"], 6)
        form.setFieldValue(["range", "max"], 20)
        form.setFieldValue("q", 5)
    }, [form])
    // todo: 临时测试
    // const isFetching = false
    // 图表配置
    const config = {
        data: chartData,
        xField: 'x',
        yField: 'value',
        padding: "auto",
        appendPadding: [50, 0, 0, 0],
        label: {
            // 可手动配置 label 数据标签位置
            position: 'top',
            // 'top', 'bottom', 'middle',
            // 配置样式
            style: {
                fill: '#000',
                opacity: 0.6,
            },
            content: (originData) => {
                return originData.info
            },
        },
        xAxis: {
            label: {
                autoHide: true,
                autoRotate: false,
            },
        },
        meta: {
            x: {
                alias: '监控阈值',
            },
            yField: {
                alias: '有效性',
            },
            info: {
                alias: "描述"
            }
        },
    };
    const columns = (type = 1) => {
        return [
            {
                title: '档位',
                dataIndex: 'level',
                key: 'level',
                align: "center"
            },
            {
                title: '初始让分',
                key: 'initialLetGoal',
                align: "center",
                render: (_, {initialLetGoal}, index) => {
                    return `${initialLetGoal[0]} ~ ${initialLetGoal[1]}`
                }
            },
            {
                title: '监控阈值',
                dataIndex: 'threshold',
                key: 'threshold',
                align: "center"

            },
            {
                title: '有(无)效性',
                dataIndex: 'Validity',
                key: 'Validity',
                align: "center"

            },
            {
                title: '是否有效',
                key: 'isEffect',
                align: "center",
                render: (_, {isEffect}) => {
                    if (isEffect) {
                        return (
                            <div style={{width: "100%", height: "100%", display: "flex", justifyContent: "center"}}>
                                <div style={{background: "green", width: 8, height: 8, borderRadius: "100%"}}></div>
                            </div>
                        )
                    } else {
                        return (
                            <div style={{width: "100%", height: "100%", display: "flex", justifyContent: "center"}}>
                                <div style={{background: "red", width: 8, height: 8, borderRadius: "100%"}}></div>
                            </div>
                        )
                    }
                },
            },
            {
                title: '达到监控阈值的比赛场数',
                dataIndex: 'totalReach',
                key: 'totalReach',
                align: "center"
            },
            {
                title: '统计比赛场数',
                dataIndex: 'totalMatch',
                key: 'totalMatch',
                align: "center"
            },
            {
                title: '统计图表',
                key: 'action',
                align: "center",
                render: (_, record, index) => {
                    const handleClick = () => {
                        let selectData
                        if (type === 1) {
                            selectData = data.plotData1[index]
                        } else {
                            selectData = data.plotData2[index]
                        }
                        const [min, max] = data.thresholdRange
                        const newData = []
                        for (let i = min; i <= max; i++) {
                            const value = selectData[0][i - min]
                            const current = selectData[1][i - min]
                            const total = selectData[2][i - min]
                            newData.push({
                                x: String(i),
                                value: parseFloat((value).toFixed(2)),
                                info: `${(value * 100).toFixed(2)}%\n${current}/${total}`
                            })
                        }
                        setChartData(newData)
                        setIsModalOpen(true)

                    }
                    return <Button type="primary" onClick={handleClick}>查看</Button>
                },
            },
        ]
    }
    //
    const handleChange = (value) => {
        console.log(`selected ${value}`);
    };
    const handleFinish = async (value) => {
        console.log(value)
        const dateRange = dateForm.getFieldValue("dateRange").map(item => item.valueOf()).join(",")
        try {
            setData({})
            const res = await analysis({body: value, dateRange}).unwrap()
            console.log(res)
            setData(res)
        } catch (e) {
            console.log(e)
        }

    }
    const handleDateFinish = async (value) => {
        value = value.dateRange.map(item => item.valueOf()).join(",")
        console.log(value)
        let matchNames = await getAllMatchNames(value).unwrap()
        matchNames = Object.entries(matchNames)
        setMatchNames(matchNames)
    }
    const handleApply = () => {
        setEmail({
            _id: form.getFieldValue("matchName").sort().join("-"),
            dateRange: dateForm.getFieldValue("dateRange").map(item => item.valueOf()).join(","),
            data,
            matchName: form.getFieldValue("matchName"),
            range: {
                min: form.getFieldValue(["range", "min"]),
                max: form.getFieldValue(["range", "max"]),
            },
            q: form.getFieldValue("q"),
        })
    }
    const handleDownload = () => {
        console.log("xxx")
        const dateRange = dateForm.getFieldValue("dateRange").map(item => item.valueOf()).join(",")
        const value = form.getFieldsValue()
        const obj = JSON.stringify(value)
        console.log(`http://localhost:5000/download?dateRange=${dateRange}&obj=${obj}`)
        window.open(`http://localhost:5000/download?dateRange=${dateRange}&obj=${obj}`)
    }
    return (
        <div className={styles.main}>
            <h1>Step01</h1>
            <hr style={{marginBottom: 5}}/>
            <Form
                form={dateForm}
                onFinish={handleDateFinish}
                labelCol={{
                    span: 4,
                }}
                wrapperCol={{
                    span: 14,
                }}
            >
                <Form.Item
                    name="dateRange"
                    label="统计联赛范围"
                    rules={[
                        {
                            type: 'array',
                            required: true,
                            message: '请选择联赛发生范围',
                        },
                    ]}
                >
                    <RangePicker format="YYYY-MM-DD" placeholder={["开始时间", "结束时间"]}/>
                </Form.Item>
                <Form.Item label=" " colon={false} className={styles.submit}>
                    <Button type="primary" htmlType="submit" disabled={isLoading} loading={isLoading}>{isLoading ? "加载联赛数据中..." : "查询"}</Button>
                </Form.Item>

            </Form>
            <h1>Step02</h1>
            <hr style={{marginBottom: 5}}/>

            <Form
                disabled={!matchNames.length}
                form={form}
                onFinish={handleFinish}
                labelCol={{
                    span: 4,
                }}
                wrapperCol={{
                    span: 14,
                }}
            >
                <Form.Item
                    label="联赛"
                    name="matchName"
                    rules={[
                        {
                            required: true,
                            message: '请至少选择一个联赛',
                        },
                    ]}
                >
                    <Select
                        mode="multiple"
                        style={{
                            width: '100%',
                        }}
                        placeholder="请选择一个或多个联赛"
                        onChange={handleChange}
                    >
                        {
                            matchNames.map((matchName, index) => (
                                <Option value={matchName[0]} key={index}>
                                    {`${matchName[0]} ${matchName[1]}`}
                                </Option>
                            ))
                        }
                    </Select>
                </Form.Item>
                <Form.Item
                    label="监控阈值范围"
                    className={styles.range}
                    required
                >
                    <Form.Item
                        name={["range", "min"]}
                        rules={[
                            {
                                required: true,
                                message: '最小监控阈值范围不可为空',
                            },
                        ]}
                    >
                        <InputNumber/>
                    </Form.Item>
                    -
                    <Form.Item
                        name={["range", "max"]}
                        rules={[
                            {
                                required: true,
                                message: '最大监控阈值范围不可为空',
                            },
                        ]}
                    >
                        <InputNumber/>
                    </Form.Item>
                </Form.Item>
                <Form.Item
                    label="划分档位"
                    name="q"
                    rules={[
                        {
                            required: true,
                            message: '档位划分不可为空',
                        },
                    ]}
                >
                    <InputNumber/>
                </Form.Item>
                <Form.Item label=" " colon={false} className={styles.submit}>
                    <Button type="primary" htmlType="submit" disabled={isAnalysis} loading={isAnalysis}>
                        {isAnalysis ? "分析中..." : "分析"}
                    </Button>&nbsp;
                    <Button type="primary" onClick={handleApply} disabled={!Object.getOwnPropertyNames(data).length}>
                        应用到配置
                    </Button>&nbsp;
                    <Button type="primary" onClick={handleDownload} disabled={!Object.getOwnPropertyNames(data).length}>
                        下载到本地
                    </Button>
                </Form.Item>
            </Form>
            {Object.getOwnPropertyNames(data).length === 0 ? "" : (
                <>
                    <hr style={{margin: "30px 0"}}/>
                    <div style={{display: "flex", justifyContent: "space-evenly"}}>
                        <div>统计监控阈值范围：{data.thresholdRange[0]}~{data.thresholdRange[1]}</div>
                        <div>当前使用盘：{data.panName}</div>
                        <div>统计比赛数：{data.totalCount}</div>
                        <div>监控阈值触发率：{(data.reachRate * 100).toFixed(2)}%</div>
                    </div>
                    <hr style={{margin: "30px 0"}}/>

                    <Table
                        title={() => <h1 style={{margin: 0}}>增量统计</h1>}
                        columns={columns(1)}
                        dataSource={Object.entries(data.inc_table).map(item => item[1])}
                    />
                    <div style={{height: 20}}></div>
                    <Table
                        title={() => <h1 style={{margin: 0}}>减量统计</h1>}
                        columns={columns(2)}
                        dataSource={Object.entries(data.des_table).map(item => item[1])}
                    />
                </>
            )}
            <Modal
                title="分析图表"
                visible={isModalOpen}
                centered
                onCancel={() => setIsModalOpen(false)}
                footer={<Button type="primary" onClick={() => setIsModalOpen(false)}>确认</Button>}
                width={1000}
            >
                <Column {...config} />
            </Modal>
        </div>
    );
}

export default Home;