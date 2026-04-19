from topology.models import Substation, Feeder, Transformer
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.db.models import Q
from django.core.cache import cache

class GFKFilterMixin:
  def zone_filt_query(self, queryset: QuerySet, user):
    if user.control == 'admin':
      return queryset  
    if not user.zone:
      return queryset.none()
    
    cache_key = f'zone {user.zone.id} ids'
    cached_ids = cache.get(cache_key)
    if cached_ids:
      sub_ids, fdr_ids, tr_ids = cached_ids
    else:
      sub_ids = Substation.objects.filter(zone=user.zone).values_list('id', flat=True)
      fdr_ids = Feeder.objects.filter(substation__zone=user.zone).values_list('id', flat=True)
      tr_ids = Transformer.objects.filter(feeder__substation__zone=user.zone).values_list('id', flat=True)
      cache.set(cache_key, (sub_ids, fdr_ids, tr_ids), 3600)

    sub_ct = ContentType.objects.get_for_model(Substation)
    fdr_ct = ContentType.objects.get_for_model(Feeder)
    tr_ct = ContentType.objects.get_for_model(Transformer)

    return queryset.filter(
      Q(content_type=sub_ct, object_id__in=sub_ids) |
      Q(content_type=fdr_ct, object_id__in=fdr_ids) |
      Q(content_type=tr_ct, object_id__in=tr_ids)
    )