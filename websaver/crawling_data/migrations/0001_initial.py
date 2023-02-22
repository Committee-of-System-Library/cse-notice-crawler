# Generated by Django 4.0.6 on 2023-02-22 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('link', models.URLField()),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('saved_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('status', models.CharField(default='NEW', max_length=3)),
            ],
        ),
    ]
