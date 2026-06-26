from tortoise import migrations
from tortoise.migrations import operations as ops
from models.enums.role import RoleEnum
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_auto_20260609_1537')]

    initial = False

    operations = [
        ops.CreateModel(
            name='CharacterCollection',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('author', fields.ForeignKeyField('models.Character', source_field='author_id', db_constraint=True, to_field='id', related_name='authored_collections', on_delete=OnDelete.CASCADE, null=True)),
                ('characters', fields.ManyToManyField('models.Character', unique=True, db_constraint=True, through='charactercollection_character', forward_key='character_id', backward_key='charactercollection_id', related_name='member_collections', on_delete=OnDelete.CASCADE)),
                ('title', fields.CharField(max_length=256)),
                ('description', fields.TextField(unique=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={'table': 'charactercollection', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='User',
            name='role',
            field=fields.CharEnumField(default=RoleEnum.USER, description='ADMIN: admin\nUSER: user', enum_type=RoleEnum, max_length=5),
        ),
    ]
