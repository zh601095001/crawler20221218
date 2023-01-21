const {MongoClient} = require("mongodb")

const mongoClient = await MongoClient.connect(process.env.DATABASE_URI)
const database = mongoClient.db( "defaultDb")
const collection = database.collection("defaultCollection")
const cur = req.collection.find(extraQuery).skip(skip).limit(limit)
