from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
#from . import views
from pharmacy.views import PharmacyRegistrationView,PharmacyLoginView,SubscriptionPlanView,LogOutView,ForgetPasswordView,RestPasswordView,PharmacyProfileView,MedicineDetailes,MedicineInfo,submitSubscriptionView,OffersDetailes

urlpatterns=[

  path('register/',PharmacyRegistrationView.as_view(),name='PharmacyRegister'),
  path('login/',PharmacyLoginView.as_view(),name='login'),
  path('profile/', PharmacyProfileView.as_view(), name='profile'),
  path('editProfile/', PharmacyProfileView.as_view(), name='profile'),
  path('resetPassword/', RestPasswordView.as_view(), name='resetPassword'),
  path('forgetPassword/', ForgetPasswordView.as_view(), name='forgetPassword'),
  path('medicines/',MedicineDetailes.as_view(),name='medicine'),
  path('medicines/<int:id>/',MedicineInfo.as_view()),
  path('medicines/<int:id>/offers/',OffersDetailes.as_view(),name='offers'),
  # path('offers/',OffersInfo.as_view(),name='offers'),
  #re_path(r'^$', views.home, name='index'),
  # path('subscriptionToken/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
  # path('subscriptionToken/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
  path('submitSubscription/',submitSubscriptionView.as_view()),
  path('logout/',LogOutView.as_view(),name='logout'),
  path('creatSubPlan/',SubscriptionPlanView.as_view(),name='logout'),
  
  
  ]
