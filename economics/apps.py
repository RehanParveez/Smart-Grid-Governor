from django.apps import AppConfig

class EconomicsConfig(AppConfig):
    name = 'economics'
    
    def ready(self):
      import economics.signals
