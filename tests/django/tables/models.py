from django.db import models


class DjangoTable(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField()

    class Meta:
        db_table = "table"
        ordering = ("id",)
