# region				-----External Imports-----
from django.urls import path

# region				-----Internal Imports-----
from . import views

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


urlpatterns = [
    path("satellites/", views.SatellitesView.as_view(), name="satellites"),
    path("satellite/login/", views.LoginView.as_view(), name="login-satellite"),
    path("signup/success/", views.SignUpView.as_view(), name="signup-success"),
]
