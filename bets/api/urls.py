# region				-----External Imports-----
from rest_framework import routers

# region				-----Internal Imports-----
from .frontend import views as frontend_restful

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion

frontend_router = routers.DefaultRouter()

frontend_router.register(viewset=frontend_restful.OddsAmountViewSet, prefix="frontend/odds-amount")
frontend_router.register(viewset=frontend_restful.TradeViewSet, prefix="frontend/trades")
urlpatterns = frontend_router.urls
