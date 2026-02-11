from ..client.api import urls as client_urls
from ..satellite.api import urls as satellite_urls
from ..user.api import urls as user_urls

urlpatterns = (
    user_urls.frontend_router.urls
    + client_urls.frontend_router.urls
    + satellite_urls.frontend_router.urls
)
