# Generated by Django 4.2.21 on 2025-05-20 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredient_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Добавьте изображение рецепта', upload_to='', verbose_name='Картинка рецепта'),
        ),
    ]
