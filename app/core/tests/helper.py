from django.contrib.auth import get_user_model


def create_user(email='test@example.com', password='testpass123', **args):
    return get_user_model().objects.create_user(
        email=email, password=password, **args)
