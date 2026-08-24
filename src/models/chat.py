from tortoise import fields, models

from models.enums.message_role import MessageRoleEnum


class Chat(models.Model):
    id = fields.UUIDField(primary_key=True)

    character = fields.ForeignKeyField('models.Character', related_name='chats')
    user = fields.ForeignKeyField('models.User', related_name='chats')

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'chat'


class Message(models.Model):
    """
    Full chat log. The sliding window that is actually sent to the model
    is cached in Redis, see api.v1.chat_logic.layer.ChatLayer
    """

    id = fields.BigIntField(primary_key=True) 

    chat = fields.ForeignKeyField('models.Chat', related_name='messages', db_index=True)

    role = fields.CharEnumField(MessageRoleEnum, max_length=16)
    content = fields.TextField()

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'message'
        ordering = ('id',)
