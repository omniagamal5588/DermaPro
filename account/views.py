from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import UserRegistrationSerializer,UserLoginSerializer, UserProfileSerializer,ResetPasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer
from django.contrib.auth import authenticate
from account.renders import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import jwt, datetime
from rest_framework.exceptions import AuthenticationFailed
from account.models import User
#from rest_framework.renderers import JSONRenderer, YAMLRenderer
# Create your views here.

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


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
  
  user = User.objects.filter(id=payload['id']).first()
  if not user:
    raise AuthenticationFailed('User Account not found!')
  
  return user




class UserRegistrationView(APIView):
  renderer_classes=[UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        return Response({"success":True, 'message':'Registration Successfully'}, status=status.HTTP_201_CREATED)
    # print(serializer.errors)
    return Response({'request name'}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
  def post(self, request):
    serializer = UserLoginSerializer(data=request.data)

    if 'email' not in request.data and 'password' not in request.data:
      return Response({"errors": {"email": ["this field is required"], "password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'email' not in request.data:
      return Response({"errors": {"email": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'password' not in request.data:
      return Response({"errors": {"password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()

    if user is None:
      raise AuthenticationFailed('User not found!')

    if not user.check_password(password):
      raise AuthenticationFailed('Incorrect password!')

    payload = {
      'id': user.id,
      'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
      'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')

    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'token': token,
        'login': True,
    }
    return response
   

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  # permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    user=isLogin(request) 
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  

   
  def put(self,request,format=None):
    user=isLogin(request)
    serializer= UserProfileSerializer(user,data=request.data)
    if serializer.is_valid(raise_exception=True):
        pharmacy = serializer.save()
        return Response({'msg':'profile updated Successfully',"success":True}, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
   
      

class RestPasswordView(APIView):
  renderer_classes = [UserRenderer]
  # permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    # serializer = ResetPasswordSerializer(data=request.data, context={'user':request.user})
    if 'old_password' not in request.data and 'new_password' not in request.data:
      return Response({"errors": {"old_password": ["this field is required"], "new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'old_password' not in request.data:
      return Response({"errors": {"old_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif 'new_password' not in request.data:
      return Response({"errors": {"new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
    
    old_password = request.data['old_password']
    new_password = request.data['new_password']
    user=isLogin(request)
    flag = user.check_password(old_password)

    if not flag:
      return Response({"errors": {"old_password": ["this field is invalid"]}}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"success":True, "message": "Password is Rest Successfully"}, status=status.HTTP_200_OK)

#ForgetPassword For User
class ForgetPasswordView(APIView):
  renderer_classes=[UserRenderer]
  def put(self,request,formt=None):
       if 'email' not in request.data:
        return Response({"errors": {"email": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
       
       elif 'new_password' not in request.data:
        return Response({"errors": {"new_password": ["this field is required"]}}, status=status.HTTP_400_BAD_REQUEST)
  
       email = request.data['email']
       new_password = request.data['new_password']
       user = User.objects.filter(email=email).first()
       if not user:
        raise AuthenticationFailed('User Account not found!')
       user.set_password(new_password)
       user.save()
       return Response({"success":True, "message": "Password is changed Successfully"}, status=status.HTTP_200_OK)


class LogOutView(APIView):
   def post(self, request, format=None):
    user = isLogin(request)
    response_data = {"message": "LogOut Successfully !", "success":True}
    response = Response(response_data)
    response.delete_cookie('jwt')
    return response
