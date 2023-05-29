import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from pharmacy.serializers import PharmacyRegistrationSerializer,PharmacyProfileSerializer,ResetPasswordSerializerPharma,SubscriptionPlanSerializer,PharmacyMedicineSerializer,MedicineSerializer,OfferSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pharmacy.renders import PharmacyRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed
from pharmacy.models import Pharmacy,Medicine,Offers,Subscription,Subscription_Pharmacy,Pharmacy_medicine,Subscription_Pharmacy
from django.http import JsonResponse
from rest_framework.decorators import api_view
#from rest_framework.renderers import JSONRenderer, YAMLRenderer
# Create your views here.

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

def getSubscriotionToken(user, sub_type, startDate, endDate):
  payload = {
    'id': user.id,
    'subscription_id':sub_type.id,
    'exp': endDate,
    'iat': startDate,
    'role': "subscribe"
  }
  token = jwt.encode(payload, 'secret', algorithm='HS256')
  return token

def isLogin(request):
  token = request.META.get('HTTP_AUTHORIZATION')
  if not token:
    raise AuthenticationFailed('Authentication credentials were not provided.')
  try:
    payload = jwt.decode(token, 'secret', algorithms=['HS256'])
  except jwt.ExpiredSignatureError:
    raise AuthenticationFailed('Authentication credentials were not provided.')
  
  except jwt.exceptions.DecodeError:
    raise AuthenticationFailed('Invalid token')


  user = Pharmacy.objects.filter(id=payload['id']).first()
  if not user:
    raise AuthenticationFailed('User Account not found!')
  
  return user

def isSubscribe(request):
  token =request.META.get('HTTP_AUTHORIZATION')
  if not token:
    raise AuthenticationFailed('Authentication credentials were not provided.')
  try:
    payload = jwt.decode(token, 'secret', algorithms=['HS256'])
  except jwt.ExpiredSignatureError:
    raise AuthenticationFailed('Subscription is Expired')
  
  except jwt.exceptions.DecodeError:
    raise AuthenticationFailed('Invalid token')
  
  user = Pharmacy.objects.filter(id=payload['id']).first()
  if not user:
    raise AuthenticationFailed('User Account not found!')
  elif payload['role'] !="subscribe":
    raise AuthenticationFailed("You aren't Authorized, you must make Subscription")
  
  return user
  
#PharmacyRegisterView
class PharmacyRegistrationView(APIView):
   renderer_classes=[PharmacyRenderer]
   def post(self, request, format=None):
    serializer = PharmacyRegistrationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        pharmacy = serializer.save()
        return Response({'msg':'Registration Of Pharmacy Successfully',"success":True}, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


#login Pharmacy View
class PharmacyLoginView(APIView):
  def post(self, request):
    if 'email' not in request.data and 'password' not in request.data:
      return Response({"errors": {"email": ["this field is required"], "password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'email' not in request.data:
      return Response({"errors": {"email": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'password' not in request.data:
      return Response({"errors": {"password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    email = request.data['email']
    password = request.data['password']

    pharmacy = Pharmacy.objects.filter(email=email).first()

    if pharmacy is None:
        raise AuthenticationFailed('Pharmacy Account not found!')

    if not pharmacy.check_password(password):
        raise AuthenticationFailed('Incorrect password!')
    
    payload = {
          'id': pharmacy.id,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
          'iat': datetime.datetime.utcnow(),
          'role': "login"
      }

    loginToken = jwt.encode(payload, 'secret', algorithm='HS256')

    subscribed = Subscription_Pharmacy.objects.filter(pharmacy_id=pharmacy).last()
    if subscribed :
      subToken = getSubscriotionToken(pharmacy, subscribed.subscription_id, subscribed.start_date, subscribed.end_date)
      
      try:
         token= jwt.decode(subToken, 'secret', algorithms=['HS256'])
      except jwt.ExpiredSignatureError:
        token = loginToken

      token = subToken
    else: 
      token = loginToken
    
    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'token': token,
        'login': True
    }
    return response

# pharmacy profile
class PharmacyProfileView(APIView):
  renderer_classes = [PharmacyRenderer]
  # permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    user = isSubscribe(request)
    serializer = PharmacyProfileSerializer(user)
    return Response({"success": True , "data":serializer.data}, status=status.HTTP_200_OK)

  def put(self, request, format=None):
    user = isSubscribe(request)
    serializer = PharmacyProfileSerializer(user, data=request.data)
    if serializer.is_valid(raise_exception=True):
        pharmacy = serializer.save()
        return Response({'msg':'profile updated Successfully',"success":True}, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


#changePassword for pharmacy
class RestPasswordView(APIView):
  renderer_classes = [PharmacyRenderer]
  def post(self, request, format=None):
    if 'old_password' not in request.data and 'new_password' not in request.data:
      return Response({"errors": {"old_password": ["this field is required"], "new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    # elif 'email' not in request.data:
    #   return Response({"errors": {"email": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'old_password' not in request.data:
      return Response({"errors": {"old_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'new_password' not in request.data:
      return Response({"errors": {"new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    old_password = request.data['old_password']
    user = isSubscribe(request)
    new_password = request.data['new_password']
    flag = user.check_password(old_password)

    if not flag:
      return Response({"errors": {"old_password": ["this field is invalid"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    return Response({"success":True, "message": "Password is Rest Successfully"}, status=status.HTTP_200_OK)

#ForgetPassword for pharmacy
class ForgetPasswordView(APIView):
   renderer_classes = [PharmacyRenderer]
   def put(self,request,formt=None):
       if 'email' not in request.data:
        return Response({"errors": {"email": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
       
       elif 'new_password' not in request.data:
        return Response({"errors": {"new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
  
       email = request.data['email']
       new_password = request.data['new_password']
       user = Pharmacy.objects.filter(email=email).first()
       if not user:
        raise AuthenticationFailed('Pharmacy Account not found!')
       user.set_password(new_password)
       user.save()
       return Response({"success":True, "message": "Password is changed Successfully"}, status=status.HTTP_200_OK)
 

#Logout Api View:
class LogOutView(APIView):
   def get(self, request, format=None):
    user = isLogin(request)
    response_data = {"message": "LogOut Successfully !", "success":True}
    response = Response(response_data)
    response.delete_cookie('jwt')
    return response
   
#Subscription View
class submitSubscriptionView(APIView):
  def post(self,request,format=None):
    user = isLogin(request)
    if 'subscription_id' not in request.data:
      return Response({'success':False,'subscription_id':'subscription_id is Requried'})
    
    sub_type=Subscription.objects.filter(id=request.data["subscription_id"]).first()
    if not sub_type:
       return Response ({'success':False,'msg':'Subscription Type not Avabliable'})
    
    payload = {
        'pharmacy_id': user.id,
        'subscription_id':sub_type.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=sub_type.duration),
        'iat': datetime.datetime.utcnow(),
        'role': "subscribe"

    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    
    end=datetime.datetime.utcnow()+datetime.timedelta(days=sub_type.duration) 
    start =datetime.datetime.utcnow()
    Subscription_Pharmacy.objects.create(pharmacy_id=user,subscription_id=sub_type,start_date=start,end_date=end)
    return JsonResponse({"msg":"the subscription done",'subscriptionToken':token,'success':True})
    # return JsonResponse({"error":"the user is not authorized to do it"})    

#Crud Opertaion For Medicine APIView
class MedicineDetailes(APIView):
   serializer_class=MedicineSerializer

  #  get all medicine of the login pharmacy
   def get(self,request):
      user = isSubscribe(request)
      data=Pharmacy_medicine.objects.filter(pharmacy_id=user)
      medicines = [record.medicine_id for record in data]
      serializer=MedicineSerializer(medicines, many=True)

      return Response({"success":True, "data":serializer.data},status=status.HTTP_200_OK)
   

  #  create medicine
   def post(self,request):
      serializer=MedicineSerializer(data=request.data)
      user = isSubscribe(request)
      if serializer.is_valid():
         medicine=Medicine.objects.filter(serial_number=request.data['serial_number']).first()
         if not medicine:
            medicine=serializer.save()
         exist= Pharmacy_medicine.objects.filter(pharmacy_id=user,medicine_id=medicine).first()
         if exist:
            return Response({'success':False,"msg":"Medicine Is Already Exist"},status=status.HTTP_400_BAD_REQUEST)
         Pharmacy_medicine.objects.create(pharmacy_id=user,medicine_id=medicine)    
         return Response({"msg":"Medicine Succesfully Added",'success':True},status=status.HTTP_201_CREATED)
      
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#Medicine Section
#For Get&Put&Patch&Delete On object
class MedicineInfo(APIView):
   def get(self,request,id):
      user = isSubscribe(request)
      try:
         obj=Medicine.objects.get(id=id)
      except Medicine.DoesNotExist:
         msg={"msg":"This Medicine Type Not Found", "success":False} 
         return Response(msg,status=status.HTTP_404_NOT_FOUND)
      serializer =MedicineSerializer(obj)
      return Response({"success":True, "data":serializer.data},status=status.HTTP_200_OK)

   def put(self,request,id):
      user = isSubscribe(request)
      try:
         obj=Medicine.objects.get(id=id)
      except Medicine.DoesNotExist:
         msg={"msg":"Not Found ", "success": False}
         return Response(msg,status=status.HTTP_404_NOT_FOUND)
      serializer =MedicineSerializer(obj,data=request.data)
      if serializer.is_valid():
         medicine=Medicine.objects.filter(serial_number=request.data['serial_number']).first()
         if medicine:
            return Response({'success':False,"msg":"Is Already Exist"},status=status.HTTP_400_BAD_REQUEST)
         serializer.save()
         return Response({"success":True ,"data":serializer.data},status=status.HTTP_205_RESET_CONTENT)
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
   

   def delete(self,request,id):
      user = isSubscribe(request)
      try:
         obj=Medicine.objects.get(id=id)
      except Medicine.DoesNotExist:
         msg={"msg":"Medicine Not Found", "success":False}
         return Response(msg,status=status.HTTP_404_NOT_FOUND)
      obj.delete()
      return Response({"msg":"deleted successfully", "success":True},status=status.HTTP_204_NO_CONTENT)
   
#Offers Section

#Crud Opertions for for Offers
class OffersDetailes(APIView):
   #serializer_class=MedicineSerializer
   
   def get(self,request):
      user = isSubscribe(request)
      obj=Offers.objects.all()
      serializer=OfferSerializer(obj,many=True)
      return Response(serializer.data,status=status.HTTP_200_OK)
   
   def post(self,request,id):
      user = isSubscribe(request)
      exist= Pharmacy_medicine.objects.filter(pharmacy_id=user,medicine_id=id).first()
      if not exist:
        return Response({'success':False,'msg':"You Do'nt Have this Medicine"},status=status.HTTP_400_BAD_REQUEST)
      
      entryData={"pharmacy_id"}
      serializer=PharmacyMedicineSerializer(exist,data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response({'success':True,'msg':'offer is added'},status=status.HTTP_201_CREATED)
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
   
#For Get&Put&Patch&Delete On object
class OfferInfo(APIView):
    def get(self,request,id):
        user = isSubscribe(request)
        try:
          obj=Offers.objects.get(id=id)
        except Offers.DoesNotExist:
          msg={"msg":"This Offer Post Not Found"} 
          return Response(msg,status=status.HTTP_404_NOT_FOUND)
        serializer =OfferSerializer(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,id):
        user = isSubscribe(request)
        try:
          obj=Offers.objects.get(id=id)
        except Offers.DoesNotExist:
          msg={"msg":"Not Found "}
          return Response(msg,status=status.HTTP_404_NOT_FOUND)
        serializer =OfferSerializer(obj,data=request.data)
        if serializer.is_valid():
          serializer.save()
          return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        user = isSubscribe(request)
        try:
          obj=Offers.objects.get(id=id)
        except Offers.DoesNotExist:
          msg={"msg":"Not Found"}
          return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"msg":"deleted"},status=status.HTTP_204_NO_CONTENT)


class SubscriptionPlanView(APIView):
  #createSubscriptionPlan
  def post(self,request,format=None):
    #  user = isSubscribe(request)
    serializer=SubscriptionPlanSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({"success":True, "data":serializer.data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



   


