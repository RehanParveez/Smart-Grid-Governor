from accounts.tests import ParentTest
from topology.models import Grid, Substation, Feeder, Transformer, Branch
from resources.models import FuelType, PowerSource, GenerationUnit, GenerationRecord
from economics.models import FeedFinanHealth
from decimal import Decimal
from accounts.models import User
from analytics.models import Sustainability, Efficiency
from analytics.services import LoadForecaster, AnalyticsService, SustainabilityCheck
from django.test import TestCase
from economics.models import BillingAcc, PaymentRec, FeedFinanHealth
from resources.models import FuelType, PowerSource, GenerationUnit
from rest_framework.test import APITestCase
from django.urls import reverse

# class AnalyticsServiceTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.sub = Substation.objects.create(zone=self.zone_a, name = 'Alpha Sub', max_capa_mw=250.0)
#     self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-ANLYTC')
#     self.fuel = FuelType.objects.create(name = 'Solar', renewable=True)
#     self.source = PowerSource.objects.create(grid_zone=self.zone_a, name = 'Solar Station Alpha', location = 'North Sector', owner_type = 'private')
#     self.unit = GenerationUnit.objects.create(source=self.source, unit_name = 'Unit-1', fuel_type=self.fuel, installed_capacity_mw=150.0, cost_per_unit=Decimal('18.50'))

#   def test_sustainability_calculation(self):
#     FeedFinanHealth.objects.create(feeder=self.feeder, tot_defecit=Decimal('1000.00'))
#     Sustainability.objects.create(zone=self.zone_a, curr_deficit=Decimal('2000.00'), improv_rate=0)
#     rec = SustainabilityCheck.calc_debt(self.zone_a)
#     self.assertEqual(rec.curr_deficit, Decimal('1000.00'))
#     self.assertEqual(rec.improv_rate, Decimal('50.00'))
#     self.assertTrue(rec.is_sustainable)

#   def test_load_predict(self):
#     GenerationRecord.objects.create(unit=self.unit, output_mw=Decimal('100.00'))
#     predic = LoadForecaster.predict(self.zone_a)
#     self.assertEqual(predic.predi_peak_dem_mw, Decimal('110.00'))
#     self.assertEqual(predic.predi_shortfall_mw, Decimal('10.00'))
#     self.assertEqual(predic.confi_score, 85)

#   def test_analy_effic_upd(self):
#     effic_rec = AnalyticsService.upd_efficiency(zone=self.zone_a, total_collected=Decimal('80.00'), total_expected=Decimal('100.00'))
#     self.assertEqual(effic_rec.effic_ratio, Decimal('80.00'))
#     self.assertEqual(effic_rec.tot_mw_suppl, Decimal('250.00'))

#   def test_sustainab_no_prev_rec(self):
#     FeedFinanHealth.objects.create(feeder=self.feeder, tot_defecit=Decimal('580.00'))
#     rec = SustainabilityCheck.calc_debt(self.zone_a)
#     self.assertEqual(rec.improv_rate, Decimal('0.00'))
#     self.assertFalse(rec.is_sustainable)
    
class AnalyticsSignalTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(username = 'citizen', email = 'cit@gmail.com', password = 'cit12312')
    self.zone = Grid.objects.create(name = 'Central Grid', description = 'the central grid of bwp')
    self.sub = Substation.objects.create(zone=self.zone, name = 'Sub A', max_capa_mw=250.0)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-21', curr_load_mw=Decimal('10.00'))
    self.trans = Transformer.objects.create(feeder=self.feeder, kva_rating=500)
    self.branch = Branch.objects.create(transformer=self.trans, type = 'residential')
    self.account = BillingAcc.objects.create(user=self.user, branch=self.branch, balance = '25000.00')
    self.fuel = FuelType.objects.create(name = 'Hydro', renewable=True)
    self.source = PowerSource.objects.create(grid_zone=self.zone, name = 'Dam 1', location = 'Valley', owner_type = 'state')
    self.unit = GenerationUnit.objects.create(source=self.source, unit_name = 'H-Unit', fuel_type=self.fuel, 
      installed_capacity_mw=100.0, cost_per_unit=Decimal('10.00'))

  def test_pay_trigg_analy(self):
    payment_amount = Decimal('750.00')
    PaymentRec.objects.create(account=self.account, amount_paid=payment_amount, reference_id = 'REF-PAY-999')
    health = FeedFinanHealth.objects.get(feeder=self.feeder)
    self.assertEqual(health.reco_percent, Decimal('50.00'))
    self.assertEqual(health.tot_defecit, Decimal('750.00'))
    efficiency = Efficiency.objects.get(zone=self.zone)
    self.assertEqual(efficiency.tot_rev_expec, Decimal('750.00'))
    self.assertEqual(efficiency.tot_rev_collec, Decimal('50.00'))

class AnalyticsViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.eff_record = Efficiency.objects.create(zone=self.zone_a, tot_mw_suppl=Decimal('100.00'), tot_rev_expec=Decimal('5000.00'),
      tot_rev_collec=Decimal('4500.00'), effic_ratio=Decimal('90.00'))
    self.list_url = reverse('efficiency-list')

  def test_admin_access_all_effic(self):
    self.client.force_authenticate(user=self.admin)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.data[0]['zone_name'], 'zone 1')

  def test_consumer_access_denied(self):
    self.client.force_authenticate(user=self.consumer)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 403)

  def test_zone_filtering_logic(self):
    self.client.force_authenticate(user=self.admin)
    Efficiency.objects.create(zone=self.zone_b, tot_mw_suppl=50, tot_rev_expec=10, tot_rev_collec=5, effic_ratio=50)
    resp = self.client.get(self.list_url, {'zone_id': self.zone_a.id})
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['zone_name'], 'zone 1')