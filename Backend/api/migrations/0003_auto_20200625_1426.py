# Generated by Django 3.0.7 on 2020-06-25 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200615_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight', to=settings.AUTH_USER_MODEL),
        ),
    ]
