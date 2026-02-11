from django.contrib.auth.mixins import LoginRequiredMixin


class SatelliteRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            request.user.satellite
            return self.handle_no_permission()
        except:
            return super().dispatch(request, *args, **kwargs)
