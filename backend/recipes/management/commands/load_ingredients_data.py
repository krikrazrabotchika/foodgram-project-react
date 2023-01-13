import json
import os
from django.core.management import BaseCommand
from tqdm import tqdm
from typing import Any, Optional
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Класс команды для загрузки данных
    игнредиентов из json файла.
    """
    filename: str = 'ingredients'
    ext: str = '.json'
    path_to_file: str = os.path.join('static', 'data', filename + ext)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        if Ingredient.objects.exists():
            self.stdout.write(
                'Initial data '
                '\033[0;33;48m{}\033[0;0m '
                'already exists.'.format(self.filename)
            )
            return

        with open(self.path_to_file, 'rb') as fin:
            data: list[dict[str, str]] = json.load(fin)

            for entry in tqdm(data):
                ingredient = Ingredient()
                ingredient.name = entry.get('name')
                ingredient.measurement_unit = entry.get('measurement_unit')
                ingredient.save()

        return self.stdout.write(
            'Loading \033[1m{}\033[0m data successfully done.'
            .format(self.filename)
        )
