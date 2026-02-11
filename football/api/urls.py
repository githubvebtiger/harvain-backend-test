# region				-----External Imports-----
from rest_framework import routers

# region				-----Internal Imports-----
from .frontend import views as frontend_restful

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion

frontend_router = routers.DefaultRouter()

frontend_router.register(
    viewset=frontend_restful.BestFixtureViewSet, prefix="frontend/best-fixture"
)

frontend_router.register(
    viewset=frontend_restful.LeagueViewSet,
    prefix="frontend/league",
    basename="frontend-league",
)

urlpatterns = frontend_router.urls
