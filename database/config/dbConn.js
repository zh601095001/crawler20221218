const mongoose = require('mongoose');
const argv = require('minimist')(process.argv.slice(2))

const connectDB = async () => {
	try {
		await mongoose.connect(argv.db || process.env.DATABASE_URI, {
			useUnifiedTopology: true,
			useNewUrlParser: true,
			user: "root",
			pass: "example"
		});
	} catch (err) {
		console.error(err);
	}
}

module.exports = connectDB