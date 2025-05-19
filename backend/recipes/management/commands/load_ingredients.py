import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.conf import settings


class Command(BaseCommand):
    help = 'Load ingredients from CSV file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR.parent, 'data', 'ingredients.csv')
        abs_path = os.path.abspath(file_path)

        with open(abs_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            count = 0
            for row in reader:
                name = row[0]
                unit = row[1]
                Ingredient.objects.get_or_create(name=name, measurement_unit=unit)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} ingredients'))
