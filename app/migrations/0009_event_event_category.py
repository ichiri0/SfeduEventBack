# Generated by Django 5.0 on 2023-12-23 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_eventcategory_alter_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.eventcategory'),
        ),
    ]