import re

from tortoise.models import Model
from tortoise import fields, validators


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=100)
    email = fields.CharField(
        null=False,
        max_length=100,
        validators=[
            validators.RegexValidator(
                "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", re.I
            ),
        ],
    )
    profile_url = fields.CharField(max_length=100)
    flags = fields.IntField(default=0)
