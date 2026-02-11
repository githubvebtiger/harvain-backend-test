# region				-----External Imports-----
from django.db import models

# endregion

# region				-----Internal Imports-----
# endregion

# region			  -----Supporting Variables-----
# endregion


class Country(models.Model):
    title = models.CharField(
        verbose_name="Country", max_length=50, unique=True, blank=False, null=False
    )

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Countries"
        verbose_name = "Country"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return self.title

    # endregion
