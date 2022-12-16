const nodemailer = require("nodemailer");

async function sendEmail({to, subject, content}) {
    let transporter = nodemailer.createTransport({
        host: process.env.EMAIL_HOST,
        port: process.env.EMAIL_PORT,
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASSWORD,
        }
    });
    let mailOptions = {
        from: `"Basketball Info" <${process.env.EMAIL_USER}>`,
        to: to,
        subject: subject,
        html: content
    };

    const res = await transporter.sendMail(mailOptions);
    return {
        SucceedID: res.messageId
    }

}

module.exports = {
    sendEmail
}
