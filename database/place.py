from tortoise.models import Model
from tortoise import fields
from interface.place import PlaceSleepType


class Place(Model):
    place_id = fields.CharField(max_length=100)
    display_name = fields.CharField(max_length=100)
    sleep_available = fields.SmallIntField(default=PlaceSleepType.unknown.value)
    safe_rating = fields.IntField(default=3)  # 기본값 3
