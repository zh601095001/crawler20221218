const {MongoClient} = require("mongodb");
const mongoClient = await MongoClient.connect(process.env.DATABASE_URI, {connectTimeoutMS: 2 * 60 * 1000})
const database = mongoClient.db("defaultDb")
const collection = database.collection("proxy")
collection.insertOne([{
    '_id': 'b593ad42cda026f3c9a7feb34944822f',
    'http': '222.95.180.3:17768',
    'created': 1674924703,
    'isAlive': True,
    'lastModify': 1674924703
}, {'_id': '361b90f3aec68582176e630f2c2118b4', 'http': '114.216.164.234:15038', 'created': 1674924703, 'isAlive': True, 'lastModify': 1674924703}, {
    '_id': '0a2dda19cf07bef0b0d2b2c3c97ab1c4',
    'http': '223.240.209.239:18590',
    'created': 1674924703,
    'isAlive': True,
    'lastModify': 1674924703
}, {'_id': '31b69b8efbbc2c72dda0419b0235e7cc', 'http': '113.103.128.249:16791', 'created': 1674924703, 'isAlive': True, 'lastModify': 1674924703}, {
    '_id': '824546ae48dd4d63dd5bf1af68caa58c',
    'http': '114.104.135.178:23830',
    'created': 1674924703,
    'isAlive': True,
    'lastModify': 1674924703
}, {'_id': '386608e16b389a9ed87fc5d3f145f7af', 'http': '140.250.91.152:22167', 'created': 1674924703, 'isAlive': True, 'lastModify': 1674924703}, {
    '_id': 'ba597b848a2749389829b4587bac8794',
    'http': '183.166.125.77:17592',
    'created': 1674924703,
    'isAlive': True,
    'lastModify': 1674924703
}])