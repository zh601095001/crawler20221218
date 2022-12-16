const {MongoClient} = require("mongodb")
const mongodb = async (req, res, next) => {
    const {db, collection, ...extras} = req.query
    const mongoClient = await MongoClient.connect(process.env.DATABASE_URI)
    const database = mongoClient.db(db ? db : "defaultDb")
    req.collection = database.collection(collection ? collection : "defaultCollection")
    req.query = extras
    req.mongoClient = mongoClient
    next();
}
module.exports = mongodb