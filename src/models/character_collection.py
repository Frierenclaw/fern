from tortoise import fields, models


class CharacterCollection(models.Model):
    id = fields.UUIDField(pk=True)

    author = fields.ForeignKeyField('models.Character',
                                    related_name='authored_collections')
    characters = fields.ManyToManyField('models.Character',
                                        related_name='member_collections')
    
    title = fields.CharField(max_length=256)
    description = fields.TextField(max_length=2048)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)