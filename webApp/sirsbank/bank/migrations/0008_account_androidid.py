# Generated by Django 3.1.4 on 2020-12-10 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0007_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='androidID',
            field=models.CharField(default='', max_length=200),
        ),
    ]
