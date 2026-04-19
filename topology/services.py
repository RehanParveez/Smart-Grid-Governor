from topology.models import Feeder, Transformer, Branch
from topology.models import Grid
from django.core.cache import cache

class TopologyTreeService:
  @staticmethod
  def recursive_structure(zone_id):
    cache_key = f'zone {zone_id} tree'
    cached_tree = cache.get(cache_key)
    if cached_tree:
      return cached_tree
    
    grid_exists = Grid.objects.filter(id=zone_id)
    grid_exists = grid_exists.exists()
    if not grid_exists:
        return None
    grid = Grid.objects.prefetch_related('substations__feeders__transformers__branches').get(id=zone_id)
    
    substation_list = []
    for sub in grid.substations.all():
      feeder_list = []
      for f in sub.feeders.all():
            
        transformer_list = []
        for t in f.transformers.all():    
          branch_list = []
          for b in t.branches.all():
            branch_list.append({'id': b.id, 'account_number': b.account_number, 'type': b.type,
              'is_energized': b.is_energized})
            
          transformer_list.append({'id': t.id, 'uid': t.uid, 'kva_rating': t.kva_rating, 'is_energized': t.is_energized,
            'branches': branch_list})
          

        status_label = 'SHEDDING'
        if f.is_energized:
          status_label = 'ACTIVE'
        feeder_list.append({'id': f.id, 'code': f.code, 'status': status_label, 'curr_load_mw': f.curr_load_mw,
          'transformers': transformer_list})
      substation_list.append({'id': sub.id, 'name': sub.name, 'feeders': feeder_list})

    data = {'grid_name': grid.name, 'substations': substation_list}
    cache.set(cache_key, data, 7200)
    return data
    
  @staticmethod
  def feeder_power(feeder, requested_by):
    if requested_by.control not in ['admin', 'engineer']:   
      return None
    if feeder.is_shedding_active == True:
      feeder.is_shedding_active = False
      feeder.is_energized = True
    else:
      feeder.is_shedding_active = True
      feeder.is_energized = False
        
    feeder.save()
    return feeder

  @staticmethod
  def branch_children(branch_type, branch_id):
    if branch_type == 'substation':
      return Feeder.objects.filter(substation_id=branch_id)
    if branch_type == 'feeder':
      return Transformer.objects.filter(feeder_id=branch_id)     
    if branch_type == 'transformer':
      return Branch.objects.filter(transformer_id=branch_id)
            
    return []