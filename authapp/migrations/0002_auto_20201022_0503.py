# Generated by Django 3.1.2 on 2020-10-22 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationmodel',
            name='date_of_birth',
            field=models.DateTimeField(help_text='MM/DD/YYYY'),
        ),
    ]