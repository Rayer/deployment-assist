import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_email(subject, sender, receiver_list, content, snapshot_log=None):
    if snapshot_log is None:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(receiver_list)
    else:
        msg = MIMEMultipart(
            From=sender,
            To=COMMASPACE.join(receiver_list),
            Date=formatdate(localtime=True),
            Subject=subject
        )

        msg.attach(MIMEText(content))
        msg.attach(MIMEApplication(snapshot_log, Content_Disposition='attachment; filename="snapshot_logs.tar.gz"',
                                   Name='snapshot_logs.tar.gz'))


    s = smtplib.SMTP('172.17.17.30', 25)
    s.sendmail(sender, receiver_list, msg.as_string())
    s.quit()

if __name__ == '__main__':
    send_email('Hello', 'sanity-test@kvm01.local', ['dl-tdc-eng-nms-scg-app@ruckuswireless.com','rayer.tung@ruckuswireless.com'], 'Hello Testing')
