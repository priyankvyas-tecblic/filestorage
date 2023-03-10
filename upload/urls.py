from django.urls import path
from upload import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path('upload/',views.UploadApi.as_view(),name="Upload File"),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('register/', views.Register.as_view(), name='register User'),
    path('Verified/<uid>/<token>/',views.UserPasswordResetView.as_view(),name="reset password with Mail"),
    path('download/<int:id>', views.download, name='register User'),
    path('deletefile/<int:id>', views.UploadApi.as_view(), name='delete File'),
    path('logout/', views.LogOutView.as_view(), name='Logout User'),
    
]
    