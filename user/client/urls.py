# region				-----External Imports-----
from django.urls import path

# region				-----Internal Imports-----
from . import views

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


urlpatterns = [path("client/login/", views.LoginView.as_view(), name="login-client")]
