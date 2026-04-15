from django.apps import AppConfig

class PrioritizationConfig(AppConfig):
    name = 'prioritization'
    
    def ready(self):
      import prioritization.signals
