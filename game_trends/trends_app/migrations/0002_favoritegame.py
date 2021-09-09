# Generated by Django 2.2 on 2021-09-09 00:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trends_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ManyToManyField(related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]