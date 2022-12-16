const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const testSchema = new Schema({
    a: {
        type: String,
        required: true
    },
    b: {
        type: String,
        required: true
    }
});

module.exports = mongoose.model('Test', testSchema);