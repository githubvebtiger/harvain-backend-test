# region				-----External Imports-----
from django.urls import path
from rest_framework import routers

# region				-----Internal Imports-----
from .frontend import views as frontend_restful

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion

frontend_router = routers.DefaultRouter()

frontend_router.register(
    viewset=frontend_restful.RequisitesViewSet, prefix="frontend/requisites"
)
