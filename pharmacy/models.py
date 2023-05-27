from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.utils import timezone


#  Custom User Manager
class UserManager(BaseUserManager):
  def create_user(self, email, name, location, phone_number, description,pharmacy_image ,password=None):
      """
      Creates and saves a User with the given email, name, tc and password.
      """
      if not email:
        raise ValueError('User must have an email address')

      user = self.model(
          email=self.normalize_email(email),
         name=name,
         location=location,
         phone_number=phone_number,
         description=description,
         pharmacy_image = pharmacy_image
         
      )
      user.set_password(password)
      user.save(using=self._db)
      return user

  def create_superuser(self, email, name, location,phone_number,description, pharmacy_image, password=None):
      """
      Creates and saves a superuser with the given email, name, tc and password.
      """
      user = self.create_user(
          email=self.normalize_email(email),
          password=password,
          name=name,
          location=location,
          phone_number=phone_number,
          description=description,
          pharmacy_image=pharmacy_image
          

      )
      user.is_admin = True
      user.save(using=self._db)
      return user
      
#  Custom User Model
class Pharmacy(AbstractBaseUser):
  email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
  )
  name=models.CharField(max_length=200, verbose_name='Name')
  location=models.CharField(max_length=200, verbose_name='Location')
  phone_number=models.CharField(max_length=15, verbose_name='Phone number')
  description=models.CharField(max_length=255,verbose_name='Description')
  pharmacy_image=models.ImageField(upload_to='img', null=False ,verbose_name='Pharmacy Image')
  is_active = models.BooleanField(default=True)
  is_superuser = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  #REQUIRED_FIELDS = ['name', 'tc']

  def __str__(self):
      return self.email
  

# Subscrition Type
# class Subscription_Type(models.Model):
#     name=models.CharField(max_length=100)

#Subscription Class
class Subscription(models.Model):
    price=models.IntegerField(null=False)
    #user = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    subscription_type = models.CharField( max_length=255,null=True)
    duration=models.IntegerField(default=0)
    
   


class Subscription_Pharmacy(models.Model):
    pharmacy_id=models.ForeignKey(Pharmacy,on_delete=models.SET_NULL,null=True )
    subscription_id=models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True)  


class Medicine(models.Model):
  serial_number=models.CharField(max_length=255 )
  medicine_image=models.ImageField(upload_to='img', null=False ,verbose_name='Medicine Image')
  medicine_name=models.CharField(max_length=255)
  medicine_description=models.TextField()
  medicine_price=models.DecimalField(max_digits=6, decimal_places=2)
  pharmacy_id=models.CharField(Pharmacy,max_length=255,default=True)
  

class Pharmacy_medicine(models.Model):
  pharmacy_id=models.ForeignKey(Pharmacy,on_delete=models.SET_NULL,null=True)
  medicine_id=models.ForeignKey(Medicine,on_delete=models.SET_NULL,null=True)

  

  def __str__(self):
    return self.medicine_name  
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



#Offers Class
class Offers(models.Model):
   offer_name=models.CharField(max_length=255)
   offer_image=models.ImageField(upload_to='img',null=False,verbose_name='Offer Image')
   offer_description=models.TextField()
   offer_previous_price=models.DecimalField(max_digits=6, decimal_places=2)
   offer_new_price=models.DecimalField(max_digits=6,decimal_places=2)

   def __str__(self):
    return self.offer_name



class Pharmacy_offers(models.Model):
   pharmacy_id=models.ForeignKey(Pharmacy,on_delete=models.SET_NULL,null=True )
   offer_id=models.ForeignKey(Offers,on_delete=models.SET_NULL,null=True )
