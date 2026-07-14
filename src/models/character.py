from tortoise import fields, models


class Character(models.Model):
    id = fields.UUIDField(pk=True)

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=2048)
    
    prompt = fields.CharField(max_length=4096)

    cover_url = fields.TextField(null=True) # URL of cover in S3
    model_url = fields.TextField(null=True) # URL of vrm in S3
    animations_url = fields.TextField(null=True) # URL of vrma in S3
    
    created_by = fields.ForeignKeyField('models.User')
    created_at = fields.DatetimeField(auto_now_add=True)

    is_approved = fields.BooleanField(default=False)