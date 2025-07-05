# case/emails.py
from urllib import request

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_donation_confirmation_email(donation):
    subject = f"Thank You for Your Donation to {donation.case.title}!"
    html_message = render_to_string('emails/donation_confirmation.html', {
        'donation': donation,
        'request': request,
        'settings': settings,
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = donation.donor.email

    if to_email:
        try:
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            print(f"Donation confirmation email sent to {to_email}")
        except Exception as e:
            print(f"Error sending donation confirmation email to {to_email}: {e}")
    else:
        print(f"No email address for donor {donation.donor.username}. Skipping confirmation email.")


def notify_case_creator_of_donation(donation):
    subject = f"New Donation Received for Your Case: {donation.case.title}"
    html_message = render_to_string('emails/creator_notification.html', {'donation': donation})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = donation.case.creator.email

    if to_email:
        try:
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            print(f"Creator notification email sent to {to_email}")
        except Exception as e:
            print(f"Error sending creator notification email to {to_email}: {e}")
    else:
        print(f"No email address for case creator {donation.case.creator.username}. Skipping notification email.")

