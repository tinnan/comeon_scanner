from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader, select_autoescape
from util.utility import CONFIG, SECRET_CONFIG
import smtplib

ENV = Environment(  # TODO add CSS style to mail template.
    loader=PackageLoader('cloud', 'mail_templates'),
    autoescape=select_autoescape(['html'])
)


def send_notification(notifications):
    send_from = CONFIG['app']['mail.from']
    send_to = CONFIG['app']['mail.to']
    msg = create_message(send_from, send_to, notifications)
    send_email(send_from, send_to, msg)


def send_email(send_from, send_to, msg):
    smtp_host = CONFIG['app']['mail.smtp.host']
    smtp_port = CONFIG['app']['mail.smtp.port']
    smtp_secure = CONFIG['app']['mail.smtp.secure']
    smtp_password = SECRET_CONFIG['secret']['mail.smtp.password']
    server = smtplib.SMTP(host=smtp_host, port=smtp_port)
    if smtp_secure == 'True':
        server.starttls()
    server.login(send_from, smtp_password)
    server.sendmail(send_from, send_to, msg.as_string())
    server.quit()


def create_message(send_from, send_to, notifications):
    # Create message container.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Comeon-book.com followed stories alert'
    msg['From'] = send_from
    msg['To'] = send_to

    # render message from template for message body.
    template = ENV.get_template('default.html')
    rendered = template.render(notifications=notifications)
    body = MIMEText(rendered, 'html')
    msg.attach(body)
    return msg
