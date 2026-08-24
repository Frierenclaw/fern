from tortoise import migrations
from tortoise.migrations import operations as ops
from models.enums.message_role import MessageRoleEnum
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0005_auto_20260714_2139')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Chat',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('character', fields.ForeignKeyField('models.Character', source_field='character_id', db_constraint=True, to_field='id', related_name='chats', on_delete=OnDelete.CASCADE)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='chats', on_delete=OnDelete.CASCADE)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'chat', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Message',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('chat', fields.ForeignKeyField('models.Chat', source_field='chat_id', db_index=True, db_constraint=True, to_field='id', related_name='messages', on_delete=OnDelete.CASCADE)),
                ('role', fields.CharEnumField(description='USER: user\nASSISTANT: assistant', enum_type=MessageRoleEnum, max_length=16)),
                ('content', fields.TextField(unique=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'message', 'app': 'models', 'pk_attr': 'id', 'table_description': 'Full chat log. The sliding window that is actually sent to the model'},
            bases=['Model'],
        ),
    ]
