import smtplib
from email.mime.text import MIMEText


def send_email(subject, sender, receiver_list, content):
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver_list[0]

    s = smtplib.SMTP('172.17.17.30', 25)
    s.sendmail(sender, receiver_list, msg.as_string())
    s.quit()

if __name__ == '__main__':
    send_email('Hello', 'sanity-test@kvm01.local', ['dl-tdc-eng-nms-scg-app@ruckuswireless.com','rayer.tung@ruckuswireless.com'], 'Hello Testing')
