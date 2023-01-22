require('dotenv').config();
const express = require('express');
const app = express();
const path = require('path');
const cors = require('cors');
const corsOptions = require('./config/corsOptions');
const {logger} = require('./middleware/logEvents');
const errorHandler = require('./middleware/errorHandler');
const cookieParser = require('cookie-parser');
const credentials = require('./middleware/credentials');
const mongodbMiddleWare = require("./middleware/mongodb")
const {createProxyMiddleware} = require('http-proxy-middleware');
const mongoose = require('mongoose');
const connectDB = require('./config/dbConn');
const argv = require('minimist')(process.argv.slice(2))
const PORT = argv.port || process.env.PORT || 3500;

// proxy
app.use(
    "/settings",
    createProxyMiddleware({
        target: "http://localhost:8000/db",
        changeOrigin: true,
        pathRewrite: {'^/settings': ''},
        proxyTimeout: 60 * 60 * 1000
    })
)
app.use(
    "/analysis",
    createProxyMiddleware({
        target: process.env.ANALYSIS_URL,
        changeOrigin: true,
        pathRewrite: {'^/analysis': ''},
        proxyTimeout: 60 * 60 * 1000

    })
)
// Connect to MongoDB
// connectDB();

app.use(mongodbMiddleWare)

// custom middleware logger
app.use(logger);
//
// Handle options credentials check - before CORS!
// and fetch cookies credentials requirement
app.use(credentials);

// Cross Origin Resource Sharing
app.use(cors(corsOptions));

// built-in middleware to handle urlencoded form data
app.use(express.urlencoded({extended: false}));

// built-in middleware for json
app.use(express.urlencoded({extended: true, limit: "20mb"}));
app.use(express.json({extended: true, limit: "20mb"}));


app.use(express.json());

// app.use(bodyParser())

//middleware for cookies
app.use(cookieParser());

//serve static files
app.use('/', express.static(path.join(__dirname, '/public')));

// routes
app.use("/docs", require("./routes/swaggerUI"))
app.use('/', require('./routes/root'));
app.use("/db", require("./routes/db"))

app.all('*', (req, res) => {
    res.status(404);
    if (req.accepts('html')) {
        res.sendFile(path.join(__dirname, 'views', '404.html'));
    } else if (req.accepts('json')) {
        res.json({"error": "404 Not Found"});
    } else {
        res.type('txt').send("404 Not Found");
    }
});

app.use(errorHandler);

// mongoose.connection.once('open', () => {
//     const DB_URL = argv.db || process.env.DATABASE_URI
//     console.log(`Connected to MongoDB ${DB_URL}`);
//     app.listen(PORT, () => {
//         const host = 'http://localhost'
//         console.log(`Server running at ${host}:${PORT}\nDocs: ${host}:${PORT}/docs`)
//     });
// });
app.timeout = 30 * 60 * 1000 //  超时时间 30min
app.listen(PORT, () => {
    const host = 'http://localhost'
    console.log(`Server running at ${host}:${PORT}\nDocs: ${host}:${PORT}/docs`)
});