const nodemailer = require("nodemailer");

async function sendEmail({emailHost, emailPort, emailUser, emailPassword, to, subject, content}) {
    let transporter = nodemailer.createTransport({
        host: emailHost,
        port: emailPort,
        auth: {
            user: emailUser,
            pass: emailPassword,
        }
    });
    let mailOptions = {
        from: `"Basketball Info" <${emailUser}>`,
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
