import React from 'react';
import {Route, Routes} from "react-router-dom";
import NotFound from "./pages/NotFound";
import MyLayout from "./layouts/MyLayout";
import Home from "./pages/Home";
import Settings from "./pages/Settings";

function App() {
    return (
        <Routes>
            <Route path="/" element={<MyLayout/>}>
                <Route index element={<Home/>}/>
                <Route path="setting" element={<Settings/>}/>
            </Route>
            <Route path="/*" element={<NotFound/>}/>
        </Routes>
    );
}

export default App;
