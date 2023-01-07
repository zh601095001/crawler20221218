(function () {
    const data = pageObj.data
    return JSON.stringify(data.filter(item => {
        const matchstate = parseInt(item.matchstate)
        return matchstate > 0
    }))
})
()