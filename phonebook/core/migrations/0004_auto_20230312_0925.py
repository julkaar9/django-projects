# Generated by Django 3.2.5 on 2023-03-12 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_phonedirectory_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'contact', 'verbose_name_plural': 'contacts'},
        ),
        migrations.AlterModelOptions(
            name='phonedirectory',
            options={'verbose_name': 'Phone instance', 'verbose_name_plural': 'Phone directory'},
        ),
        migrations.AlterModelOptions(
            name='spamdata',
            options={'verbose_name': 'spam', 'verbose_name_plural': 'spam items'},
        ),
    ]
