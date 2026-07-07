from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0003_auto_20260624_0457')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='CharacterCollection',
            name='author',
            field=fields.ForeignKeyField('models.Character', source_field='author_id', db_constraint=True, to_field='id', related_name='authored_collections', on_delete=OnDelete.CASCADE),
        ),
        ops.AddField(
            model_name='User',
            name='created_at',
            field=fields.DatetimeField(auto_now=False, auto_now_add=True),
        ),
    ]
