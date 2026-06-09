from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Character',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('name', fields.CharField(max_length=128)),
                ('description', fields.CharField(max_length=2048)),
                ('prompt', fields.CharField(max_length=4096)),
                ('cover_url', fields.TextField(null=True, unique=False)),
                ('model_url', fields.TextField(null=True, unique=False)),
                ('created_by', fields.ForeignKeyField('models.User', source_field='created_by_id', db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('is_approved', fields.BooleanField(default=False)),
            ],
            options={'table': 'character', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
