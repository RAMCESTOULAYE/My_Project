from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
# import redis  # Décommente si tu utilises Redis

APPLICATIONS = ['users', 'orders']

# Décommente et configure si tu utilises Redis pour la blacklist
# BLACKLIST = redis.StrictRedis.from_url(settings.CACHES["jwt_tokens"]["LOCATION"])

def send_password_reset_email(user, template_name):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Utilisation d'une URL dynamique pour l'environnement de production front
    reset_url = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"

    message = render_to_string(template_name, {
        'user': user,
        'reset_url': reset_url,
    })

    send_mail(
        subject="Please reset your password",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )

# Si tu utilises Redis, décommente ces fonctions et la variable BLACKLIST ci-dessus
# def is_token_blacklisted(token):
#     """
#     Vérifie si un token JWT est blacklisté.
#     """
#     return BLACKLIST.get(token) is not None

# def blacklist_token(token, expiration):
#     """
#     Ajoute un token JWT à la blacklist avec une durée d'expiration.
#     """
#     if not BLACKLIST.get(token):  # Si le token n'est pas déjà blacklisté
#         BLACKLIST.setex(token, expiration, "Token blacklisted!")