const {createProxyMiddleware} = require("http-proxy-middleware");
module.exports = function (app) {
    app.use(
        "/settings",
        createProxyMiddleware({
            target: "http://localhost:8000/db",
            changeOrigin: true,
            pathRewrite: {'^/settings': ''}

        })
    )
    app.use(
        "/analysis",
        createProxyMiddleware({
            target: "http://localhost:5000",
            changeOrigin: true,
            pathRewrite: {'^/analysis': ''}
        })
    )

};