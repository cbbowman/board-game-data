# Generated by Django 2.2 on 2021-09-11 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trends_app', '0009_game_game_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='growth',
            field=models.SmallIntegerField(default=0),
        ),
    ]
