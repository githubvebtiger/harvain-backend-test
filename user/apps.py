# region				-----External Imports-----
from django.apps import AppConfig

# endregion

# region				-----Internal Imports-----
# endregion


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name_plural = "Users"
    verbose_name = "User"
    name = "user"

    def ready(self):
        import user.signals
        import user.tasks
        
        # Run safe startup data sync
        from .startup_sync import run_startup_sync
        
        # Use a small delay to ensure all apps are loaded
        import threading
        import time
        
        def delayed_sync():
            time.sleep(2)  # Wait 2 seconds for full app initialization
            run_startup_sync()
        
        # Run sync in background thread to not block app startup
        sync_thread = threading.Thread(target=delayed_sync, daemon=True)
        sync_thread.start()
