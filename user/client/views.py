# region				-----External Imports-----
from django import http, views
from django.contrib.auth import authenticate, login

# region				-----Internal Imports-----
from . import forms
from .models import Client

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class LoginView(views.View):
    def post(self, request, *args, **kwargs):
        login_type = request.POST.get("login-type", "master")
        if login_type != "satellite":
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        form = forms.ClientLoginForm(request.POST)
        if not form.is_valid():
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        if not user:
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        try:
            client = user.client
        except Client.DoesNotExist:
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        login(request, user)

        return http.JsonResponse({"message": "Success"}, status=200)
