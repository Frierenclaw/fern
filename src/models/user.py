from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)

    full_name = fields.CharField(max_length=256)
    email = fields.CharField(max_length=256, unique=True)
    
    password = fields.BinaryField()