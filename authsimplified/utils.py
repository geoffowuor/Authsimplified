import pyotp
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def send_code_to_user(request, email):
    """
    Generates/stores an otp secret on the user (if missing), sends an OTP email,
    and sets a session key 'authsimplified_user_email' for the verification flow.
    """
    user = User.objects.get(email=email)

    if not user.secret_key:
        user.secret_key = pyotp.random_base32()

    # default interval seconds (configurable in settings)
    OTP_INTERVAL = getattr(settings, "AUTHSIMPLIFIED_OTP_INTERVAL", 300)
    otp_instance = pyotp.TOTP(user.secret_key, interval=OTP_INTERVAL)
    otp = otp_instance.now()

    # store email in session for verification steps
    if request is not None:
        request.session["authsimplified_user_email"] = email

    current_site = getattr(settings, "AUTHSIMPLIFIED_SITE_NAME", "Your Site")
    subject = getattr(settings, "AUTHSIMPLIFIED_SUBJECT", "Email Verification Code")
    context = {"user": user, "otp": otp, "current_site": current_site, "interval": OTP_INTERVAL}

    html_content = render_to_string("authsimplified/otp_email_template.html", context)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)
    send_email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=from_email,
        to=[email],
    )
    send_email.content_subtype = "html"
    send_email.send(fail_silently=False)

    user.otp_created_at = timezone.now()
    user.save()
