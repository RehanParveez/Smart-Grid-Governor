from django.apps import AppConfig

class TopologyConfig(AppConfig):
  name = 'topology'
    
  def ready(self):
    import topology.signals
