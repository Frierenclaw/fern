from tortoise import migrations
from tortoise.migrations import operations as ops
from orjson import loads
from tortoise.fields.base import OnDelete
from tortoise.fields.data import JSON_DUMPS
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0004_auto_20260708_0019')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Client',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='clients', on_delete=OnDelete.CASCADE)),
                ('app_version', fields.CharField(max_length=32)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={'table': 'client', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='ClientFunction',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('client', fields.ForeignKeyField('models.Client', source_field='client_id', db_constraint=True, to_field='id', related_name='functions', on_delete=OnDelete.CASCADE)),
                ('name', fields.CharField(max_length=128)),
                ('description', fields.TextField(unique=False)),
                ('input_schema', fields.JSONField(encoder=JSON_DUMPS, decoder=loads)),
            ],
            options={'table': 'client_functions', 'app': 'models', 'unique_together': (('client', 'name'),), 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='Character',
            name='animations_url',
            field=fields.TextField(null=True, unique=False),
        ),
    ]
