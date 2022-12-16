const path = require('path');
const swaggerUi = require("swagger-ui-express");
const router = require("express").Router()
const fs = require("fs");

const openapi = JSON.parse(fs.readFileSync(path.join(__dirname, "../docs/openapi.json")).toString())
router.use('/', swaggerUi.serve);
router.get('/', swaggerUi.setup(openapi, {
    customCss: '.swagger-ui .topbar { display: none }',
    // explorer: true
}));
router.get('/swagger.json', function (req, res) {
    res.setHeader('Content-Type', 'application/json');
    res.send(openapi);
});

module.exports = router