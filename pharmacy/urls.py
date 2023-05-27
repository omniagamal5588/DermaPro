from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
#from . import views
from pharmacy.views import PharmacyRegistrationView,PharmacyLoginView,LogOutView,RestPasswordView,PharmacyProfileView,MedicineDetailes,MedicineInfo,submit_subscription,OffersDetailes

urlpatterns=[

  path('pharmacyRegister/',PharmacyRegistrationView.as_view(),name='PharmacyRegister'),
  path('pharmacyLogin/',PharmacyLoginView.as_view(),name='login'),
  path('pharmacyProfile/', PharmacyProfileView.as_view(), name='profile'),
  path('resetPassword/', RestPasswordView.as_view(), name='resetPassword'),
  path('medicine/',MedicineDetailes.as_view(),name='medicine'),
  path('med/<int:id>/',MedicineInfo.as_view()),
  path('offers/',OffersDetailes.as_view(),name='offers'),
  #re_path(r'^$', views.home, name='index'),
  path('subscriptionToken/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('subscriptionToken/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
  path('submit_subscription/',submit_subscription),
  path('logout/',LogOutView.as_view(),name='logout'),
  
  ]