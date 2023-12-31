# Generated by Django 5.0 on 2023-12-22 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_stage', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
            },
        ),
        migrations.RemoveField(
            model_name='group',
            name='group_name',
        ),
        migrations.AddField(
            model_name='group',
            name='group_course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.groupcourse'),
            preserve_default=False,
        ),
    ]
