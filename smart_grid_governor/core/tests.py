from accounts.tests import ParentTest 
from django.core.cache import cache
from topology.models import Substation, Feeder
from tasks.models import Maintenance
from smart_grid_governor.core.mixins import GFKFilterMixin
from django.contrib.contenttypes.models import ContentType

class GFKFilterMixinTest(ParentTest):
  def setUp(self):
    super().setUp()
    cache.clear()
    self.sub_a = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=50)
    self.feeder_a = Feeder.objects.create(substation=self.sub_a, code = 'FDR-A')
    self.sub_b = Substation.objects.create(zone=self.zone_b, name = 'Sub B', max_capa_mw=50)
    self.task_sub_a = Maintenance.objects.create(subject = 'Substation A Repair', branch=self.sub_a)
    self.task_fdr_a = Maintenance.objects.create(subject = 'Feeder A Repair', branch=self.feeder_a)
    self.task_sub_b = Maintenance.objects.create(subject = 'Substation B Repair', branch=self.sub_b)

    class CheckView(GFKFilterMixin):
      pass
    self.mixin_logic = CheckView()
    
  def test_gfk_link_integrity(self):
    sub_ct = ContentType.objects.get_for_model(Substation)
    self.assertEqual(self.task_sub_a.content_type, sub_ct)
    self.assertEqual(self.task_sub_a.object_id, self.sub_a.id)

  def test_admin_sees_everything(self):
    query = Maintenance.objects.all()
    res = self.mixin_logic.zone_filt_query(query, self.admin)
    self.assertEqual(res.count(), 3)

  def test_zone_isola_filtering(self):
    query = Maintenance.objects.all()
    res = self.mixin_logic.zone_filt_query(query, self.engineer_a)
    self.assertEqual(res.count(), 2)
    subjects = [t.subject for t in res]
    self.assertIn('Substation A Repair', subjects)
    self.assertIn('Feeder A Repair', subjects)
    self.assertNotIn('Substation B Repair', subjects)

  def test_caching_logic(self):
    cache_key = f'zone {self.zone_a.id} ids'
    self.assertIsNone(cache.get(cache_key))
    self.mixin_logic.zone_filt_query(Maintenance.objects.all(), self.engineer_a)
    cached_data = cache.get(cache_key)
    self.assertIsNotNone(cached_data)
    sub_ids, fdr_ids, tr_ids = cached_data
    self.assertIn(self.sub_a.id, sub_ids)
    self.assertIn(self.feeder_a.id, fdr_ids)

  def test_user_without_zone_rets_none(self):
    query = Maintenance.objects.all()
    res = self.mixin_logic.zone_filt_query(query, self.consumer)
    self.assertEqual(res.count(), 0)