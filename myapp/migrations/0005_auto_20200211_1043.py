# Generated by Django 2.1.4 on 2020-02-11 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_auto_20200211_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='tag',
        ),
        migrations.AddField(
            model_name='title',
            name='tag',
            field=models.ManyToManyField(to='myapp.Tag'),
        ),
    ]
