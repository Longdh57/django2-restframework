from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.template.loader import render_to_string


def send_log_email(job_name, message_error, admin_emails):

    html_message = render_to_string('sale_portal_ingestion/mail_template/log_email.html', {
        'job_name': job_name,
        'message_error': message_error
    })

    plain_message = strip_tags(html_message)

    send_mail('Sale Portal Cronjob Log', plain_message, settings.EMAIL_HOST_USER, admin_emails,
              html_message=html_message)
