from rest_framework import serializers
from pharmacy.models import Pharmacy,Medicine,Offers,Pharmacy_medicine,Subscription
# from . import utils
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError


#PharmacyRegisterSerializer
class PharmacyRegistrationSerializer(serializers.ModelSerializer):
 
  class Meta:
    model =Pharmacy
    fields=['name','email', 'phone_number', 'location', 'password','description','pharmacy_image']
    extra_kwargs={
      'password':{'write_only':True}
    }

# Validating Password and Confirm Password while Registration
  def validate(self, attrs):
    password = attrs.get('password')
    #password2 = attrs.get('password2')
    

    email = attrs.get('email', None)
    if Pharmacy.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ('email')})
    return super().validate(attrs)
  def create(self, validate_data):
    return Pharmacy.objects.create_user(**validate_data)

#login pharmacy serializer
class PharmacyLoginSeraializer(serializers.ModelSerializer):
  class Meta:
    model=Pharmacy
    fields=['email','password']

# class PharmacyProfileSerializer(serializers.ModelSerializer):
#   class Meta:
#     model = Pharmacy
#     fields = ['name','email', 'phone_number', 'location','description','pharmacy_image']


#Pharmacy Profile
class PharmacyProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Pharmacy
    fields = ['id', 'email', 'name','location','phone_number','pharmacy_image','description']    


class ResetPasswordSerializerPharma(serializers.Serializer):
  old_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  new_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    model = Pharmacy
    fields = ['email','old_password', 'new_password']

#MedicineSerializer
class MedicineSerializer(serializers.ModelSerializer):
  class Meta:
    model=Medicine
    fields=['id','serial_number','medicine_image','medicine_name','medicine_description','medicine_price']
  
#Phamacy_medicine
class PharmacyMedicineSerializer(serializers.ModelSerializer):
  medicine_id = MedicineSerializer()
  pharmacy_id = PharmacyProfileSerializer()
  class Meta:
    model=Pharmacy_medicine
    fields=['pharmacy_id','medicine_id','offer']

#OffersSerializer
class OfferSerializer(serializers.ModelSerializer):
  offer_previous_price=serializers.DecimalField(required=True,write_only=True,max_digits=6,decimal_places=2)
  offer_new_price=serializers.DecimalField(required=True,write_only=True,max_digits=6,decimal_places=2)

  class Meta:
    model=Offers
    fields=['id','offer_name','offer_image','offer_description','offer_previous_price','offer_new_price']
  #check if previous price is not equal new price 
  def validate(self, data):
    if data['offer_previous_price'] == data['offer_new_price']:
      raise serializers.ValidationError("The two prices must be different")
    return data  

#SubscriptionPlanSerializer
class SubscriptionPlanSerializer(serializers.ModelSerializer):
  class Meta:
    model=Subscription
    fields=['id','price','subscription_type','duration']
 
