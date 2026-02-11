# region				-----External Imports-----
from django.urls import path

# region				-----Internal Imports-----
from . import views

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


urlpatterns = [
    path("basketball/", views.BasketballIndexView.as_view(), name="basketball-index"),
    path("volleyball/", views.VolleyballIndexView.as_view(), name="volleyball-index"),
    path("formula-1/", views.Formula1IndexView.as_view(), name="formula-1-index"),
    path("handball/", views.HandballIndexView.as_view(), name="handball-index"),
    path("baseball/", views.BaseballIndexView.as_view(), name="baseball-index"),
    path("hockey/", views.HockeyIndexView.as_view(), name="hockey-index"),
    path("", views.FootballIndexView.as_view(), name="football-index"),
    path("lazy-load/", views.LazyLoadView.as_view(), name="lazy-load"),
    path("rugby/", views.RugbyIndexView.as_view(), name="rugby-index"),
]
