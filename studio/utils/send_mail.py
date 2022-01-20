import threading
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from flask import current_app
sender = 'dutbit@163.com'

mail_host = 'smtp.163.com'
mail_port = 465
mail_user = sender


def send_mail(to='', content='', subject='', type='html'):
    threading.Thread(target=send_mail_thread,
                     args=(current_app._get_current_object(), to, content, subject, type)).start()


def send_mail_thread(current_app, to='', content='', subject='', type='html'):
    with current_app.app_context():
        receivers = [to]
        msg = MIMEText(content, type, 'utf-8')
        msg['From'] = "<{}>".format(sender)  # Header('DUTBIT','utf-8')
        msg['To'] = "<{}>".format(to)  # Header(to,'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        # msg['Cc'] = #Header(','.join([to]), 'utf-8')
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        # if current_app.config['DEBUG']:
        #     return
        smtpObj.login(mail_user, current_app.config['MAIL_PASS'])
        smtpObj.sendmail(sender, receivers, msg.as_string())


def send_validation_code(to='', code=''):
    content = """
        邮箱验证码是：{}
    """.format(code)
    send_mail(to=to, subject='dutbit-账户邮箱验证', content=content)


if __name__ == "__main__":
    content = """Dear Lynn Nat, 

INVOICE  #2021
STATUS: Unpaid
AMOUNT DUE: $10.00 USD
DUE DATE: 2021-06-01
GENERATE ON: 2021-05-25.

PAYMENT METHOD:
 AliPay 支付宝

 ​​​​"""
    send_mail(to='2889205153@qq.com', content=content, subject='Invoice #202105295299: Created')
