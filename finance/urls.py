# region				-----External Imports-----
from django.urls import path

# region				-----Internal Imports-----
from . import views

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


urlpatterns = [
    path(
        "transactions/refill/",
        views.TransactionsRefillView.as_view(),
        name="transactions-refill",
    ),
    path(
        "transactions/withdraw/",
        views.TransactionsWithdrawView.as_view(),
        name="transactions-withdraw",
    ),
]
