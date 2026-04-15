from django.apps import AppConfig

class MeteringConfig(AppConfig):
    name = 'metering'
    
    def ready(self):
      import metering.signals
