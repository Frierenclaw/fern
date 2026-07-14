from tortoise import fields, models


class Client(models.Model):
    id = fields.UUIDField(primary_key=True)

    user = fields.ForeignKeyField('models.User', related_name='clients')
    app_version = fields.CharField(max_length=32)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    

class ClientFunction(models.Model):
    id = fields.UUIDField(primary_key=True)
    
    client = fields.ForeignKeyField('models.Client', related_name='functions')
    name = fields.CharField(max_length=128)
    description = fields.TextField()
    input_schema = fields.JSONField() 

    class Meta:
        table = 'client_functions'
        unique_together = (('client', 'name'),)
