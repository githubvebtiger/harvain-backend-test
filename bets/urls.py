# region				-----External Imports-----
from django.urls import path

# region				-----Internal Imports-----
from . import views

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


urlpatterns = [
    path("bets/wins/", views.BetsWinsView.as_view(), name="bets-wins"),
    path("bets/losses/", views.BetsLossesView.as_view(), name="bets-losses"),
    path("bets/progress/", views.BetsProgressView.as_view(), name="bets-progress"),
]
