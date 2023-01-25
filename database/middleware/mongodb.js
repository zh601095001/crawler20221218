const {MongoClient} = require("mongodb")
const mongodb = async (req, res, next) => {
    try {
        const {db, collection, ...extras} = req.query
        const mongoClient = await MongoClient.connect(process.env.DATABASE_URI, {connectTimeoutMS: 2 * 60 * 1000})
        const database = mongoClient.db(db ? db : "defaultDb")
        req.collection = database.collection(collection ? collection : "defaultCollection")
        req.query = extras
        req.mongoClient = mongoClient
        next();
    } catch (e) {
        next(e)
    }

}
module.exports = mongodb