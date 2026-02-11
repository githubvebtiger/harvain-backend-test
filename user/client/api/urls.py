from rest_framework import routers

from .frontend import views as frontend_restful

frontend_router = routers.DefaultRouter()

frontend_router.register(viewset=frontend_restful.ClientViewSet, prefix="frontend/client")
