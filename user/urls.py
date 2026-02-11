# region				-----External Imports-----
# endregion

# region				-----Internal Imports-----
from .client import urls as client_urls
from .salesman import urls as salesman_urls
from .satellite import urls as satellite_urls
from .user import urls as user_urls

# endregion

# region			  -----Supporting Variables-----
# endregion

urlpatterns = (
    client_urls.urlpatterns
    + salesman_urls.urlpatterns
    + satellite_urls.urlpatterns
    + user_urls.urlpatterns
)
