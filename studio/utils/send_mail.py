from re import sub
import smtplib
from email.mime.text import MIMEText
from email.header import Header
sender = 'dutbit@163.com'

mail_host = 'smtp.163.com'
mail_port = 994
mail_user = sender
mail_pass = '*'


def send_mail(to='',content='',subject=''):
    receivers = [].append(to)
    msg = MIMEText(content,'plain','utf-8')
    msg['From'] = Header('DUTBIT','utf-8')
    msg['To'] = Header(to,'utf-8')
    msg['Subject'] = Header(subject,'utf-8')
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, mail_port)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender,receivers,msg.as_string())

if __name__ == "__main__":
    send_mail(to='2889205153@qq.com',content='邮件123123杠杆',subject='leverage ratio=0')