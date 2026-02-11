from django import contrib

# region				-----External Imports-----
from django.conf import settings

# endregion

# region				-----Internal Imports-----
# endregion

# region			  -----Supporting Variables-----
# endregion


def get_all_languages() -> str:
    return " ".join(settings.LANGUAGE_CODES)


class PrettyTranslatableAdmin(contrib.admin.ModelAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["languages"] = get_all_languages()
        return super(PrettyTranslatableAdmin, self).change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["languages"] = get_all_languages()
        return super(PrettyTranslatableAdmin, self).add_view(
            request,
            form_url,
            extra_context=extra_context,
        )
