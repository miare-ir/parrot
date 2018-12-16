from django.apps import AppConfig


class ParrotConfig(AppConfig):
    name = 'parrot'

    def ready(self):
        pass
