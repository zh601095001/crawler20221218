const express = require('express');
const router = express.Router();
const dbController = require("../controllers/dbController")


router.get("/", dbController.getItems)
router.post("/s", dbController.searchItem)
router.post("/", dbController.addItems)
router.put("/", dbController.modifyItems)
router.delete("/", dbController.deleteItems)
module.exports = router