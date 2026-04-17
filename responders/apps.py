from django.apps import AppConfig

class RespondersConfig(AppConfig):
    name = 'responders'
    
    def ready(self):
      import responders.signals
