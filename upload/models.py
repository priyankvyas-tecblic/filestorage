from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, user_name, password=None):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            password=password,
            user_name=user_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_name, password):
        user = self.create_user(
            email,
            password=password,
            user_name=user_name,
        )

        user.is_admin = True
        # user.is_staff = True
        user.save(using=self._db)
        return user
    
    def get_queryset(self):
        return super().get_queryset()

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email',max_length=255,unique=True)
    user_name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    USERNAME_FIELD = 'email'
    email_verified = models.BooleanField(("Email Verification") , default=False)
    REQUIRED_FIELDS = ['user_name','password']
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

def user_directory_path(instance, filename):
    return 'file/user_{0}/{1}'.format(instance.user.id, filename)
   
class UploadFile(models.Model):
    user = models.ForeignKey(User, verbose_name=("Foreign Key"), on_delete=models.CASCADE)
    file_name = models.CharField(("File Name"), max_length=80)
    date =  models.DateField(("Date"), auto_now=True, auto_now_add=False)
    time =  models.TimeField(("Time"), default=timezone.now())
    file_path = models.CharField(("FilePath"), max_length=200)