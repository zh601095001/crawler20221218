require('dotenv').config({path: '.env'})

;const {sendEmail} = require("./utils");
const {getEmails, getSettings, changeEmailState} = require("./api");

const loop = async () => {
    try {
        const emails = await getEmails(1)
        const settings = await getSettings()
        let isError = false
        for (const receiveEmail of settings.receiveEmails) {
            const htmls = emails.map(item => item.html).join("\n")
            if (htmls) {
                try {
                    await sendEmail({
                        emailHost: settings.emailHost,
                        emailPort: settings.emailPort,
                        emailUser: settings.emailUser,
                        emailPassword: settings.emailPassword,
                        to: receiveEmail,
                        subject: "篮球监控通知",
                        content: htmls
                    })
                } catch (e) {
                    isError = true
                }
            }
        }
        if (!isError) {
            for (const email of emails) {
                await changeEmailState({_id: email._id, status: 3})
            }
        }
        if (isError) {
            console.log("邮件发送失败，请检查邮件配置是否正确...")
        }
        console.log("111")
    } catch (e) {
        console.log(e)
    }
}

setInterval(loop, 1000)