import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader, select_autoescape
from main import CONFIG, SECRET_CONFIG
import time
import logging

mod_logger = logging.getLogger('src.cloud.mail')

ENV = Environment(
    loader=PackageLoader('src.cloud', 'mail_templates'),
    autoescape=select_autoescape(['html'])
)


def send_notification(notifications):
    mod_logger.info('Sending notification e-mail...')
    send_from = CONFIG['mail.from']
    send_to = CONFIG['mail.to']
    msg = create_message(send_from, send_to, notifications)
    send_email(send_from, send_to, msg)


def send_email(send_from, send_to, msg):
    smtp_host = CONFIG['mail.smtp.host']
    smtp_port = CONFIG['mail.smtp.port']
    smtp_secure = CONFIG['mail.smtp.secure']
    smtp_password = SECRET_CONFIG['secret']['mail.smtp.password']

    mod_logger.debug('SMTP host name: %s', smtp_host)
    mod_logger.debug('SMTP host port: %s', smtp_port)
    mod_logger.debug('Is host using TLS: %s', 'Yes' if smtp_secure == 'True' else 'No')
    mod_logger.info('Sending from: %s', send_from)
    mod_logger.debug('Login password: %s', smtp_password)
    mod_logger.info('Sending to: %s', send_to)

    server = smtplib.SMTP(host=smtp_host, port=smtp_port)
    if smtp_secure == 'True':
        server.starttls()
    server.login(send_from, smtp_password)

    server.sendmail(send_from, send_to, msg.as_string())
    mod_logger.info('Notification e-mail is sent.')
    server.quit()


def create_message(send_from, send_to, notifications):
    # Create message container.
    mod_logger.debug('Creating notification e-mail...')
    msg = MIMEMultipart('alternative')
    subject = '[TINN Self notify][Comeon-book.com]Followed stories alert {}'.format(
        time.strftime("%d/%m/%y %H:%M"))
    mod_logger.debug('E-mail subject = %s', subject)
    msg['Subject'] = subject
    msg['From'] = send_from
    msg['To'] = send_to

    # render message from template for message body.
    mod_logger.debug('Loading and render e-mail template...')
    template = ENV.get_template('default.html')
    rendered = template.render(notifications=notifications)
    body = MIMEText(rendered, 'html')
    mod_logger.debug('E-mail template rendering completed.')
    msg.attach(body)
    return msg
