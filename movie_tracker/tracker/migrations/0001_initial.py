# Generated by Django 5.1.6 on 2025-03-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('tmdb_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('omdb_id', models.CharField(blank=True, max_length=20, null=True)),
                ('genre', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.CharField(blank=True, max_length=50, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('overview', models.TextField(blank=True, null=True)),
                ('trailer_id', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('tmdb_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('omdb_id', models.CharField(blank=True, max_length=20, null=True)),
                ('genre', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.CharField(blank=True, max_length=50, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('first_air_date', models.DateField(blank=True, null=True)),
                ('overview', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
