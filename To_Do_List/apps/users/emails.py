"""Email utilities for user authentication and notifications."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_welcome_email(user_email: str, username: str) -> None:
    """Send welcome email to newly registered user."""
    subject = "Welcome to Todo List!"
    html_message = render_to_string(
        "emails/welcome.html",
        {
            "username": username,
            "site_name": "Todo List",
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_verification_email(user_email: str, verification_url: str) -> None:
    """Send email verification link to user."""
    subject = "Verify your email address"
    html_message = render_to_string(
        "emails/email_verification.html",
        {
            "verification_url": verification_url,
            "site_name": "Todo List",
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user_email: str, reset_url: str) -> None:
    """Send password reset link to user."""
    subject = "Reset your password"
    html_message = render_to_string(
        "emails/password_reset.html",
        {
            "reset_url": reset_url,
            "site_name": "Todo List",
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )
