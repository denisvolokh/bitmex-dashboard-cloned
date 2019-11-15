from django.apps import AppConfig
from celery import Celery

app = Celery("app-celery")

class BitmexConfig(AppConfig):
    name = 'bitmex'

    def ready(self):
        import bitmex.signals

        app.config_from_object('django.conf:settings', force=True)