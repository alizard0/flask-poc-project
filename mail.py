import smtplib
import email
import email.encoders
import email.mime.text


class MailServer(object):
    def __init__(self, toRecipientList, mail, password, smtp='smtp.gmail.com'):
        self.smtp = smtp
        self.password = password
        self.mail = mail
        self.toRecipientList = toRecipientList
        self.msg = email.MIMEMultipart.MIMEMultipart()

    def message(self, body, subject):
        self.msg['From'] = self.mail
        self.msg['To'] = ', '.join(self.toRecipientList)
        self.msg['Date'] = email.Utils.formatdate(localtime=True)
        self.msg['Subject'] = subject
        self.msg.attach(email.MIMEText.MIMEText(body, 'html'))

    def send_email(self):
        # The actual mail send
        server = smtplib.SMTP(self.smtp, 587)
        server.ehlo()
        server.starttls()
        server.login(self.mail, self.password)
        server.sendmail(self.mail, self.toRecipientList, self.msg.as_string())
        server.quit()
