from tortoise import fields, models

from models.enums.role import RoleEnum


class User(models.Model):
    id = fields.UUIDField(pk=True)

    full_name = fields.CharField(max_length=256)
    email = fields.CharField(max_length=256, unique=True)
    
    role = fields.CharEnumField(RoleEnum,
                                default=RoleEnum.USER)
    password = fields.BinaryField()
