# trademind_app/apps.py
from django.apps import AppConfig
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


_signals_connected = False

def _create_profile_safe(user):
    lock_id = f"create_profile_lock_{user.pk}"
    if cache.add(lock_id, "true", timeout=10):
        try:
            from .models import TraderProfile
            TraderProfile.objects.get_or_create(
                user=user,
                defaults={'trader_type': 'day'}
            )
            print(f"[Signal] Profile created for {user.username}")
        except Exception as e:
            print(f"[Signal] Failed: {e}")
        finally:
            cache.delete(lock_id)
    else:
        print(f"[Signal] Duplicate blocked for {user.pk}")

def _save_user_profile(instance, **kwargs):
    try:
        if hasattr(instance, 'traderprofile'):
            instance.traderprofile.save()
    except Exception as e:
        print(f"[Signal] Save error: {e}")

class TrademindAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trademind_app'

    def ready(self):
        global _signals_connected
        if not _signals_connected:
            post_save.connect(create_user_profile, sender='auth.User')
            post_save.connect(save_user_profile, sender='auth.User')
            _signals_connected = True
            print("[Signal] Signals connected")

@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: _create_profile_safe(instance))

#User
@receiver(post_save, sender='auth.User')
def save_user_profile(sender, instance, **kwargs):
    _save_user_profile(instance)