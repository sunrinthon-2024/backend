from tortoise.models import Model
from tortoise import fields


class RaidReport(Model):
    raid_id = fields.BigIntField(pk=True, generated=True)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    area_level_name = fields.CharField(max_length=50)
    alert_type = fields.CharField(max_length=20)
    start_time = fields.DatetimeField()
    comment = fields.TextField()
