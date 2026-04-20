from django.test import TestCase
from topology.models import Grid, Substation, Feeder, Transformer, Branch
from decimal import Decimal
from metering.models import BranchMeter, MeterReading, LossAbnormality
from metering.services import EnergyAuditService
from responders.models import Team, Capability
from django.core.cache import cache
from tasks.models import Maintenance, Investigation
from accounts.tests import ParentTest
from django.urls import reverse

class MeteringServiceTest(TestCase):
  def setUp(self):
    self.zone = Grid.objects.create(name = 'Zone 3', description = 'this is the central zone')
    self.sub = Substation.objects.create(zone=self.zone, name = 'Sub-1', max_capa_mw=100)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-001', curr_load_mw=Decimal('0.00'))
    self.t1 = Transformer.objects.create(feeder=self.feeder, uid = 'T1', kva_rating=500)
    self.t2 = Transformer.objects.create(feeder=self.feeder, uid = 'T2', kva_rating=500)
    self.feeder_meter = BranchMeter.objects.create(branch=self.feeder, meter_serial = 'M-FEEDER-023')
    self.t1_meter = BranchMeter.objects.create(branch=self.t1, meter_serial = 'M-T1')
    self.t2_meter = BranchMeter.objects.create(branch=self.t2, meter_serial = 'M-T2')

  def test_detect_loss_high_sever(self):
    feeder_read = MeterReading.objects.create(meter=self.feeder_meter, energy_in_kwh=Decimal('100.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t1_meter, energy_in_kwh=Decimal('30.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t2_meter, energy_in_kwh=Decimal('20.00'), energy_out_kwh=0)
    abnorma = EnergyAuditService.detect_loss(self.feeder, feeder_read)
    self.assertIsNotNone(abnorma)
    self.assertEqual(abnorma.severity, 'high')
    self.assertEqual(abnorma.loss_percentage, Decimal('50.00'))
    self.assertEqual(LossAbnormality.objects.count(), 1)

  def test_upd_load_cache(self):
    branch_node = Branch.objects.create(transformer=self.t1, account_number = 'ACC-101')
    consumer_meter = BranchMeter.objects.create(branch=branch_node, meter_serial = 'M-CONS-1')
    new_read = MeterReading.objects.create(meter=consumer_meter, energy_in_kwh=Decimal('5.00'), energy_out_kwh=0)
    EnergyAuditService.upd_load(consumer_meter, new_read)
    self.feeder.refresh_from_db()
    self.assertEqual(float(self.feeder.curr_load_mw), 5.0)
    
  def test_detect_loss_med_sever(self):
    feeder_read = MeterReading.objects.create(meter=self.feeder_meter, energy_in_kwh=Decimal('100.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t1_meter, energy_in_kwh=Decimal('40.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t2_meter, energy_in_kwh=Decimal('30.00'), energy_out_kwh=0)
    abnormality = EnergyAuditService.detect_loss(self.feeder, feeder_read)
    self.assertIsNotNone(abnormality)
    self.assertEqual(abnormality.severity, 'medium')
    self.assertEqual(abnormality.loss_percentage, Decimal('30.00'))

  def test_detect_loss_low_sever(self):
    feeder_read = MeterReading.objects.create(meter=self.feeder_meter, energy_in_kwh=Decimal('100.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t1_meter, energy_in_kwh=Decimal('45.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t2_meter, energy_in_kwh=Decimal('40.00'), energy_out_kwh=0)
    abnormality = EnergyAuditService.detect_loss(self.feeder, feeder_read)
    self.assertIsNotNone(abnormality)
    self.assertEqual(abnormality.severity, 'low')

  def test_no_loss_abnorma(self):
    feeder_read = MeterReading.objects.create(meter=self.feeder_meter, energy_in_kwh=Decimal('100.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t1_meter, energy_in_kwh=Decimal('50.00'), energy_out_kwh=0)
    MeterReading.objects.create(meter=self.t2_meter, energy_in_kwh=Decimal('45.00'), energy_out_kwh=0)
    abnormality = EnergyAuditService.detect_loss(self.feeder, feeder_read)
    self.assertIsNone(abnormality)
    self.assertEqual(LossAbnormality.objects.count(), 0)
    
class MeteringSignalTest(TestCase):
  def setUp(self):
    self.zone = Grid.objects.create(name = 'Zone 4', description = 'this is zone 4 grid')
    self.sub = Substation.objects.create(zone=self.zone, name = 'Sub 4', max_capa_mw=100)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-SIG-01', curr_load_mw=Decimal('0.00'))
    self.t1 = Transformer.objects.create(feeder=self.feeder, uid = 'T-SIG-01', kva_rating=500)

  def test_signal_critical_theft_auto(self):
    team = Team.objects.create(name = 'fast response team a', zone=self.zone, is_active=True)
    Capability.objects.create(team=team, skill = 'theft')
    abnormality = LossAbnormality.objects.create(branch=self.feeder, loss_percentage=Decimal('55.00'), 
      severity = 'high')
    self.assertTrue(cache.get('GRID_LOCKDOWN_ENABLED'))
    task = Maintenance.objects.filter(assigned=team).first()
    self.assertIsNotNone(task)
    self.assertEqual(task.priority, 'high')
    investigation = Investigation.objects.get(abnorma=abnormality)
    self.assertEqual(investigation.task, task)
    self.assertEqual(investigation.finding_notes, 'the ship is trigg.')

  def test_signal_remove_load_on_del(self):
    branch_node = Branch.objects.create(transformer=self.t1, account_number = 'ACC-DEL-TEST')
    meter = BranchMeter.objects.create(branch=branch_node, meter_serial = 'M-DEL-SIGNAL')
    self.feeder.curr_load_mw = Decimal('50.00')
    self.feeder.save()
    f_key = f'feeder {self.feeder.id} load'
    cache.set(f_key, 50.0)
    reading = MeterReading.objects.create(meter=meter, energy_in_kwh=Decimal('10.00'), energy_out_kwh=0)
    reading.delete()
    self.feeder.refresh_from_db()
    self.assertEqual(float(self.feeder.curr_load_mw), 40.0)
    self.assertEqual(cache.get(f_key), 40.0)

class MeteringViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub 1', max_capa_mw=100)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-101')
    self.meter = BranchMeter.objects.create(branch=self.feeder, meter_serial = 'M-API-01')

  def test_submit_read_as_engineer(self):
    self.auth(self.engineer_a)
    url = reverse('metering-submit-reading')
    data = {'meter': self.meter.id, 'energy_in_kwh': '100.00', 'energy_out_kwh': '0.00'}  
    resp = self.client.post(url, data, format='json')
    self.assertEqual(resp.status_code, 201)
    self.assertEqual(resp.data['msg'], 'the reading is recor.')

  def test_active_abnorms_zone_isola(self):
    self.auth(self.engineer_a)
    LossAbnormality.objects.create(branch=self.feeder, loss_percentage=Decimal('50.00'), severity = 'high', is_verified=False)
    sub_b = Substation.objects.create(zone=self.zone_b, name = 'Sub B', max_capa_mw=150)
    feeder_b = Feeder.objects.create(substation=sub_b, code = 'F-B')
    LossAbnormality.objects.create(branch=feeder_b, loss_percentage=Decimal('60.00'), severity = 'high')
    url = reverse('metering-active-abnorms')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)

  def test_unauthorized_access(self):
    self.auth(self.consumer)
    url = reverse('metering-active-abnorms')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 403)