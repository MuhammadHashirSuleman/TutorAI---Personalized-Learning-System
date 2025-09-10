# Django signals for users app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when a user is created
    """
    if created:
        # Add any post-creation logic here
        pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save user profile when a user is saved
    """
    # Add any post-save logic here
    pass
