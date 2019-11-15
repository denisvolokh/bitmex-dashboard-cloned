from django.apps import AppConfig


class BitmexConfig(AppConfig):
    name = 'bitmex'

    def ready(self):
        import bitmex.signals