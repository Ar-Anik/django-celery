import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager

from django.db.models import signals
from main.tasks import send_verification_email
# Create your models here.

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)

        return user

class MyUser(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(verbose_name='first name', max_length=50, blank=True)
    last_name = models.CharField(verbose_name='last name', max_length=30, blank=True)
    is_verified = models.BooleanField(verbose_name='verified', default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    verification_uuid = models.UUIDField(verbose_name='Unique Verification UUID', default=uuid.uuid4)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest Possible answer: YES, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have persmission to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user member of staff?"
        # Simplest Possible answer: All admins are staff
        return self.is_admin

def user_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_verified:
        send_verification_email.delay(instance.pk)

signals.post_save.connect(user_post_save, sender=MyUser)

