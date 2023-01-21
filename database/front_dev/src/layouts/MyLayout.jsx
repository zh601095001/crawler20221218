import {Outlet, useLocation} from "react-router-dom";
import React, {useState} from 'react';
import {Layout, Menu} from "antd";
import Search from "antd/es/input/Search";
import {useNavigate} from "react-router-dom";
import {useDispatch} from "react-redux";
import {search} from "../store/searchSlice";
import styles from "./layout.module.less"


const {Header, Content, Footer} = Layout
let items = [
    {
        label: "分析",
        url: "/",
        key: "1",
    },
    {
        label: "配置",
        url: "/setting",
        key: "2"
    }
]
const getItemByKey = (key) => {
    const filterItem = items.filter(value => {
        return value.key === key
    })
    if (filterItem.length > 0) {
        return filterItem[0]
    } else {
        return null
    }
}

function MyLayout() {
    const navigate = useNavigate()
    const dispatch = useDispatch()
    const location = useLocation()
    const handleClick = ({key}) => {
        const item = getItemByKey(key)
        if (item !== null) {
            navigate(item.url)
        }
    }
    const handleSearch = (value) => {
        dispatch(search(value))
    }
    // 控制nav
    let selectedKeys
    const pathname = location.pathname
    if (pathname === "/") {
        selectedKeys = [items[0].key]
    }
    if (pathname === "/setting") {
        selectedKeys = [items[1].key]
    }


    return (
        <Layout>
            <Header className={styles.header}>
                <div className="left">
                    <div className="logo">篮球监控系统</div>
                    <Menu
                        selectedKeys={selectedKeys}
                        theme={"dark"}
                        items={items}
                        mode="horizontal"
                        style={{fontSize: 16, fontWeight: "bold", width: 300}}
                        onClick={handleClick}
                    ></Menu>
                </div>
                <div className="right">
                    {/*<Search placeholder="Search" enterButton style={{width: 400}} size="large"*/}
                    {/*        onSearch={handleSearch}/>*/}
                </div>
            </Header>
            <Content className={styles.content}>
                <Outlet/>
            </Content>
            <Footer className={styles.footer}>Powered by&nbsp;<a
                href="https://github.com/">759126132@qq.com</a>&nbsp;|&nbsp;<a
                href="https://policies.google.com/privacy">Privacy</a> </Footer>
        </Layout>

    );
}

export default MyLayout;
