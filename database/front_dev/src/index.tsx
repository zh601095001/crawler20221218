import React from 'react';
import ReactDOM from 'react-dom/client';
import {Provider} from 'react-redux';
import App from './App';
import store from "./store/store";
import {HashRouter} from "react-router-dom";
import "./index.less"
import "antd/dist/antd.min.css"
const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);
root.render(
        <Provider store={store}>
            <HashRouter>
                <App/>
            </HashRouter>
        </Provider>
);

