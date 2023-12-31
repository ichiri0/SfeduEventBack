# Generated by Django 5.0 on 2023-12-23 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_event_datetime_of_event_alter_event_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Категория Мероприятия',
                'verbose_name_plural': 'Категории Мероприятий',
            },
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='events/', verbose_name='Фото'),
        ),
    ]
