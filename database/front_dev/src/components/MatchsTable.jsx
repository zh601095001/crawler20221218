import React, {useContext, useEffect, useRef, useState} from 'react';
import {Form, Input, InputNumber, Table} from "antd";
import temp from "../data.json";

const EditableContext = React.createContext(null);
const EditableRow = ({index, ...props}) => {
    const [form] = Form.useForm();
    return (
        <Form form={form} component={false}>
            <EditableContext.Provider value={form}>
                <tr {...props} />
            </EditableContext.Provider>
        </Form>
    );
};
const EditableCell = ({
                          title,
                          editable,
                          children,
                          dataIndex,
                          record,
                          handleSave,
                          ...restProps
                      }) => {
    const [editing, setEditing] = useState(false);
    const inputRef = useRef(null);
    const form = useContext(EditableContext);
    useEffect(() => {
        if (editing) {
            inputRef.current.focus();
        }
    }, [editing]);
    const toggleEdit = () => {
        setEditing(!editing);
        form.setFieldsValue({
            [dataIndex]: record[dataIndex],
        });
    };
    const save = async () => {
        try {
            const values = await form.validateFields();
            toggleEdit();
            handleSave({
                ...record,
                ...values,
            });
        } catch (errInfo) {
            console.log('Save failed:', errInfo);
        }
    };
    let childNode = children;
    if (editable) {
        childNode = editing ? (
            <Form.Item
                style={{
                    margin: 0,
                }}
                name={dataIndex}
                rules={[
                    {
                        required: true,
                        message: `${title} is required.`,
                    },
                ]}
            >
                <InputNumber ref={inputRef} onPressEnter={save} onBlur={save}/>
            </Form.Item>
        ) : (
            <div
                className="editable-cell-value-wrap"
                style={{
                    paddingRight: 24,
                }}
                onClick={toggleEdit}
            >
                {children}
            </div>
        );
    }
    return <td {...restProps}>{childNode}</td>;
};

function MatchsTable({type, dataSource, onDataChange}) {
    // const [dataSource, setDataSource] = useState(temp)
    const tableName = type === 1 ? "inc_table" : "des_table"
    const handleSave = (row) => {
        console.log(row)
        console.log(dataSource, "source")
        dataSource[tableName][row.level] = {...dataSource[tableName][row.level], ...row}
        onDataChange({...dataSource});
    };
    const columns = [
        {
            title: '档位',
            dataIndex: 'level',
            key: 'level',
            align: "center",
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
            align: "center",
            editable: true,

        },
    ]
    const editableColumns = columns.map((col) => {
        if (!col.editable) {
            return col;
        }
        return {
            ...col,
            onCell: (record) => ({
                record,
                editable: col.editable,
                dataIndex: col.dataIndex,
                title: col.title,
                handleSave,
            }),
        };
    });
    return (
        <div>
            <Table
                title={() => {
                    if (type === 1) {
                        return <h1 style={{margin: 0}}>增量比赛</h1>
                    } else {
                        return <h1 style={{margin: 0}}>减量比赛</h1>
                    }
                }}
                components={{
                    body: {
                        row: EditableRow,
                        cell: EditableCell,
                    },
                }}
                rowClassName={() => 'editable-row'}
                bordered
                dataSource={Object.entries(dataSource[tableName]).map(item => item[1])}
                columns={editableColumns}
            />
        </div>
    );
}

export default MatchsTable;