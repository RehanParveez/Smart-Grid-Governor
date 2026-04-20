from django.test import TestCase
from topology.models import Grid, Substation, Feeder
from prioritization.models import PriorityWeight, FeedPriorScore
from decimal import Decimal
from economics.models import FeedFinanHealth
from django.contrib.contenttypes.models import ContentType
from metering.models import LossAbnormality
from prioritization.services import PriorityCalculationEngine
from accounts.tests import ParentTest
from django.urls import reverse

class PrioritizationEngineTest(TestCase):
  def setUp(self):
    self.zone = Grid.objects.create(name = 'Zone B')
    self.sub = Substation.objects.create(zone=self.zone, name = 'Sub B', max_capa_mw=140)
    PriorityWeight.objects.create(factor_name = 'recovery', weight_value=Decimal('0.7'))
    PriorityWeight.objects.create(factor_name = 'theft', weight_value=Decimal('0.7'))
    self.f1 = Feeder.objects.create(substation=self.sub, code = 'F-RICH-1') 
    self.f2 = Feeder.objects.create(substation=self.sub, code = 'F-POOR-2')

  def test_calc_logic(self):
    FeedFinanHealth.objects.create(feeder=self.f1, reco_percent=Decimal('90.00'))
    feeder_ct = ContentType.objects.get_for_model(Feeder)
    LossAbnormality.objects.create(content_type=feeder_ct, object_id=self.f1.id, loss_percentage=Decimal('20.00'), is_verified=False)
    score_obj = PriorityCalculationEngine.calc_score(self.f1)
    self.assertEqual(score_obj.final_score, Decimal('119.00'))

  def test_zone_ranking_order(self):
    FeedFinanHealth.objects.create(feeder=self.f1, reco_percent=Decimal('80.00'))
    PriorityCalculationEngine.calc_score(self.f1)
    FeedFinanHealth.objects.create(feeder=self.f2, reco_percent=Decimal('40.00'))
    PriorityCalculationEngine.calc_score(self.f2)
    PriorityCalculationEngine.upd_zone_ranks(self.zone)
    f1_score = FeedPriorScore.objects.get(feeder=self.f1)
    f2_score = FeedPriorScore.objects.get(feeder=self.f2)
    self.assertEqual(f1_score.rank_in_zone, 1)
    self.assertEqual(f2_score.rank_in_zone, 2) 
    
class PrioritizationSignalTest(TestCase):
  def setUp(self):
    self.zone = Grid.objects.create(name = 'Zone C')
    self.sub = Substation.objects.create(zone=self.zone, name = 'Sub S', max_capa_mw=140)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-SIGNAL-01')
    PriorityWeight.objects.create(factor_name = 'recovery', weight_value=Decimal('0.7'))
    PriorityWeight.objects.create(factor_name = 'theft', weight_value=Decimal('0.7'))

  def test_sign_score_upd_on_finan_save(self):
    FeedFinanHealth.objects.create(feeder=self.feeder, reco_percent=Decimal('80.00'))
    prio_score = FeedPriorScore.objects.filter(feeder=self.feeder)
    prio_score = prio_score.first()
    self.assertIsNotNone(prio_score)
    self.assertEqual(float(prio_score.final_score), 126.0)
    self.assertEqual(prio_score.rank_in_zone, 1)

  def test_sign_score_upd_on_theft_save(self):
    FeedFinanHealth.objects.create(feeder=self.feeder, reco_percent=Decimal('50.00'))
    feeder_ct = ContentType.objects.get_for_model(Feeder)
    LossAbnormality.objects.create(content_type=feeder_ct, object_id=self.feeder.id, loss_percentage=Decimal('30.00'), severity = 'medium')
    prio_score = FeedPriorScore.objects.get(feeder=self.feeder)
    self.assertEqual(float(prio_score.final_score), 84.0)
    
class PrioritizationViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=120)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-RECAL-01')
    self.list_url = reverse('priority-list')

  def test_upd_factors_admin_only(self):
    url = reverse('priority-update-factors')
    data = {'factor_name': 'theft', 'weight_value': '0.8'}
    self.auth(self.engineer_a)
    resp = self.client.post(url, data)
    self.assertEqual(resp.status_code, 403)
    self.auth(self.admin)
    resp = self.client.post(url, data)
    self.assertEqual(resp.status_code, 200)
    self.assertTrue(PriorityWeight.objects.filter(factor_name = 'theft', weight_value=0.8).exists())

  def test_recal_zone_isola(self):
    url = reverse('priority-recalculate')
    self.auth(self.engineer_a)
    data = {'zone_id': self.zone_b.id}
    resp = self.client.post(url, data)
    self.assertEqual(resp.status_code, 403)
    self.assertEqual(resp.data['err'], 'cant recal the other zone.')

  def test_recal_success(self):
    self.auth(self.engineer_a)
    url = reverse('priority-recalculate')
    data = {'zone_id': self.zone_a.id}
    resp = self.client.post(url, data)
    self.assertEqual(resp.status_code, 200)
    self.assertTrue(FeedPriorScore.objects.filter(feeder=self.feeder).exists())
