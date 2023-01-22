const status = require('http-status')
const {flatten} = require('mongo-dot-notation')
const getItems = async (req, res, next) => {
    try {
        let {limit, skip, ...extraQuery} = req.query
        limit = limit ? Number(limit) : 1000
        skip = skip ? Number(skip) : 0
        const cur = req.collection.find(extraQuery).skip(skip).limit(limit)
        const data = await cur.toArray()
        const count = await req.collection.countDocuments(extraQuery)
        await req.mongoClient.close()
        res.json({data, count, skip, limit})
    } catch (e) {
        next(e)
    } finally {
        await req.mongoClient.close()
    }
}

const searchItem = async (req, res, next) => {
    try {
        let {limit, skip, ...extraQuery} = req.body
        console.log(extraQuery)
        limit = limit ? Number(limit) : 1000
        skip = skip ? Number(skip) : 0
        const cur = req.collection.find(extraQuery).skip(skip).limit(limit)
        const data = await cur.toArray()
        const count = await req.collection.countDocuments(extraQuery)
        await req.mongoClient.close()
        res.json({data, count, skip, limit})
    } catch (e) {
        next(e)
    } finally {
        await req.mongoClient.close()
    }
}
const addItems = async (req, res, next) => {
    try {
        const data = req.body
        if (data instanceof Array) {
            return res.json(await req.collection.insertMany(data, {ordered: false}))
        }
        if (Object.prototype.toString.call(data) === "[object Object]") {
            return res.json(await req.collection.insertOne(data))
        }
    } catch (e) {
        res.status(status.CONFLICT).json({
            msg: e.toString()
        })
        next(e)
    } finally {
        await req.mongoClient.close()
    }
}
const modifyItems = async (req, res, next) => {
    const data = await req.collection.find({_id: req.body._id}).toArray()
    if (!data.length) {
        await req.collection.insertOne({_id: req.body._id})
    }
    try {
        const updateOne = async ({_id, ...extras}) => {
            return await req.collection.updateMany({_id}, flatten(extras))
        }
        if (req.body instanceof Array) {
            const info = req.body.map(item => updateOne(item))
            return res.json(await Promise.all(info))
        }
        if (Object.prototype.toString.call(req.body) === "[object Object]") {
            return res.json(await updateOne(req.body))
        }
        return res.status(status.UNPROCESSABLE_ENTITY).json({
            errMsg: "参数格式不正确"
        })
    } catch (e) {
        next(e)
    } finally {
        await req.mongoClient.close()
    }

}

const deleteItems = async (req, res, next) => {
    try {
        if (req.body instanceof Array) {
            const info = req.body.map(async item => {
                return await req.collection.deleteMany({_id: item._id})
            })
            return res.json(await Promise.all(info))
        }
        if (Object.prototype.toString.call(req.body) === "[object Object]") {
            return res.json(await req.collection.deleteMany({_id: req.body._id}))
        }
        return res.status(status.UNPROCESSABLE_ENTITY).json({
            errMsg: "参数格式不正确"
        })
    } catch (e) {
        next(e)
    } finally {
        await req.mongoClient.close()
    }


}
module.exports = {
    getItems,
    modifyItems,
    deleteItems,
    addItems,
    searchItem
}


