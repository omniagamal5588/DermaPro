from django.urls import path,include
from account.views import UserRegistrationView,UserLoginView,LogOutView,UserProfileView,RestPasswordView,ForgetPasswordView

urlpatterns=[
  path('register/',UserRegistrationView.as_view(),name='register'),
  path('login/',UserLoginView.as_view(),name='login'),
  path('profile/', UserProfileView.as_view(), name='profile'),
  path('resetPassword/', RestPasswordView.as_view(), name='resetPassword'),
  path('forgetPassword/',ForgetPasswordView.as_view(),name='forgetPassword'),
  path('editProfile/', UserProfileView.as_view(), name='profile'),
   path('logout/', LogOutView.as_view(), name='logout'),
  
  # path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
  # path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),  
]
