from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.utils import timezone

#  Custom User Manager
class UserManager(BaseUserManager):
  def create_user(self, email, first_name, last_name, phone_number, address, password=None):
      """
      Creates and saves a User with the given email, name, tc and password.
      """
      if not email:
        raise ValueError('User must have an email address')

      user = self.model(
          email=self.normalize_email(email),
         first_name=first_name,
         last_name=last_name,
         phone_number=phone_number,
         address=address,
         
      )
      user.set_password(password)
      user.save(using=self._db)
      return user

  def create_superuser(self, email, first_name, last_name,phone_number,address, password=None):
      """
      Creates and saves a superuser with the given email, name, tc and password.
      """
      user = self.create_user(
          email=self.normalize_email(email),
          password=password,
          first_name=first_name,
          last_name=last_name,
          phone_number=phone_number,
          address=address,
          

      )
      user.is_admin = True
      user.save(using=self._db)
      return user

  def create_pharmacy_account(self, email,name,phone_number,location,description,pharmacy_image, password=None):
      """
      Creates and saves a pharmacy with the given email, name, tc and password.
      """
      if not email:
          raise ValueError('pharmacy must have an email address')

      pharmacy = self.model(
          email=self.normalize_email(email),
         name=name,
         phone_number=phone_number,
         location=location,
         pharmacy_image=pharmacy_image,
         description=description
         
      )
      pharmacy.set_password(password)
      pharmacy.save(using=self._db)
      return pharmacy
  

  


    
#  Custom User Model
class User(AbstractBaseUser):
  email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
  )
  first_name=models.CharField(max_length=200, verbose_name='First name')
  last_name=models.CharField(max_length=200, verbose_name='Last name')
  phone_number=models.CharField(max_length=15, verbose_name='Phone number')
  address=models.CharField(max_length=255,verbose_name='Address')
  tc = models.BooleanField(default=True)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  #REQUIRED_FIELDS = ['name', 'tc']

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


#PharmacyTable
# class Pharmacy(AbstractBaseUser, PermissionsMixin):
   
#     name = models.CharField(max_length=30, blank=True, null=True,unique=True)
#     email = models.EmailField(max_length=250, unique=True)
#     phone_number=models.CharField(max_length=15,default=True)
#     location = models.CharField(max_length=300,  blank=True, null=True)
#     description= models.TextField(max_length=500, blank=True, null=True)
#     pharmacy_image = models.ImageField(upload_to='img', blank=True, null=True) 
#     password=models.CharField(max_length=16)

#     objects = UserManager()

#     USERNAME_FIELD = 'email'
#     #REQUIRED_FIELDS = ['email', ]

