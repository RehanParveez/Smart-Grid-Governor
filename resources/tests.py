from accounts.tests import ParentTest
from resources.models import FuelType, PowerSource, GenerationUnit, GenerationRecord
from resources.services import GenerationPlanner
from decimal import Decimal
from django.urls import reverse

# class GenerationPlannerTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.solar = FuelType.objects.create(name = 'Solar')
#     self.gas = FuelType.objects.create(name = 'Natural Gas')
#     self.solar_plant = PowerSource.objects.create(name = 'Noon Solar Park', grid_zone=self.zone_a)
#     self.gas_plant = PowerSource.objects.create(name = 'Blue Flame Thermal', grid_zone=self.zone_b)
#     GenerationUnit.objects.create(source=self.solar_plant, fuel_type=self.solar, unit_name = 'Unit S1',
#       installed_capacity_mw=Decimal('50.00'), curr_output_mw=Decimal('40.00'), cost_per_unit=Decimal('5.50'), operational=True) 
#     GenerationUnit.objects.create(source=self.gas_plant, fuel_type=self.gas, unit_name = 'Unit G1',
#       installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('80.00'), cost_per_unit=Decimal('12.00'), operational=True)
#     GenerationUnit.objects.create(source=self.gas_plant, fuel_type=self.gas, unit_name = 'Unit G2',
#       installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('0.00'), cost_per_unit=Decimal('12.00'), operational=False)

#   def test_total_supply_calcu(self):
#     stats = GenerationPlanner.total_supply()
#     self.assertEqual(stats['total_capacity'], Decimal('150.00'))
#     self.assertEqual(stats['total_actual_output'], Decimal('120.00'))

#   def test_merit_order_sorting(self):
#     merit_units = GenerationPlanner.merit_order()
#     self.assertEqual(merit_units.count(), 2) 
#     self.assertEqual(merit_units[0].unit_name, 'Unit S1')
#     self.assertEqual(merit_units[1].unit_name, 'Unit G1')

#   def test_fuel_type_breakdown(self):
#     breakdown = GenerationPlanner.fuel_type_breakdown()
#     self.assertEqual(breakdown[0]['fuel_type__name'], 'Natural Gas')
#     self.assertEqual(breakdown[0]['total_mw'], Decimal('80.00'))
#     self.assertEqual(breakdown[1]['fuel_type__name'], 'Solar')
#     self.assertEqual(breakdown[1]['total_mw'], Decimal('40.00'))
    
# class GenerationSignalTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.solar_type = FuelType.objects.create(name = 'Solar')
#     self.plant = PowerSource.objects.create(name = 'Plant Test', grid_zone=self.zone_a)

#   def test_rec_created_on_unit_creation(self):
#     unit = GenerationUnit.objects.create(source=self.plant, fuel_type=self.solar_type, unit_name = 'Unit A',
#       installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('50.00'), cost_per_unit=Decimal('10.00'))
#     record = GenerationRecord.objects.filter(unit=unit).first()
#     self.assertIsNotNone(record)
#     self.assertEqual(record.output_mw, Decimal('50.00'))

#   def test_rec_created_on_unit_upd(self):
#     unit = GenerationUnit.objects.create(source=self.plant, fuel_type=self.solar_type, unit_name = 'Unit B',
#       installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('10.00'), cost_per_unit=Decimal('10.00'))
#     unit.curr_output_mw = Decimal('85.50')
#     unit.save()
#     recs = GenerationRecord.objects.filter(unit=unit)
#     self.assertEqual(recs.count(), 2)
#     self.assertEqual(recs.first().output_mw, Decimal('85.50'))

#   def test_signal_integ_with_mult_saves(self):
#     unit = GenerationUnit.objects.create(source=self.plant, fuel_type=self.solar_type, unit_name = 'Unit Gamma',
#       installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('0.00'), cost_per_unit=Decimal('10.00'))
#     unit.curr_output_mw = Decimal('20.00')
#     unit.save()
#     unit.curr_output_mw = Decimal('40.00')
#     unit.save()
#     self.assertEqual(GenerationRecord.objects.filter(unit=unit).count(), 3)

class GeneUnitViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.solar_type = FuelType.objects.create(name = 'Solar')
    self.plant_a = PowerSource.objects.create(name = 'Zone A Solar', grid_zone=self.zone_a)
    self.unit_a = GenerationUnit.objects.create(source=self.plant_a, fuel_type=self.solar_type, unit_name = 'Unit A1',
      installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('50.00'), cost_per_unit=Decimal('5.00'))
    self.plant_b = PowerSource.objects.create(name = 'Zone B Solar', grid_zone=self.zone_b)
    self.unit_b = GenerationUnit.objects.create(source=self.plant_b, fuel_type=self.solar_type, unit_name = 'Unit B1',
      installed_capacity_mw=Decimal('100.00'), curr_output_mw=Decimal('50.00'), cost_per_unit=Decimal('5.00'))

  def test_upd_output(self):
    self.auth(self.engineer_a)
    url = reverse('generationunit-upd-output', kwargs={'pk': self.unit_a.pk})
    data = {'curr_output_mw': '75.50'}
    resp = self.client.post(url, data, format = 'json')
    self.assertEqual(resp.status_code, 200)
    self.unit_a.refresh_from_db()
    self.assertEqual(self.unit_a.curr_output_mw, Decimal('75.50'))
    self.assertEqual(resp.data['msg'], 'output is upd')

  def test_supply_status(self):
    self.auth(self.admin)
    url = reverse('generationunit-supply-status')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)
    self.assertIn('overall_stats', resp.data)
    self.assertIn('fuel_mix', resp.data)
    self.assertEqual(resp.data['overall_stats']['total_actual_output'], Decimal('100.00'))
        
  def test_zone_isola_on_upd(self):
    self.auth(self.engineer_a)
    url = reverse('generationunit-upd-output', kwargs={'pk': self.unit_b.pk})
    data = {'curr_output_mw': '99.00'}
    resp = self.client.post(url, data)
    self.assertEqual(resp.status_code, 403)

  def test_consumer_denied_access(self):
    self.auth(self.consumer)
    url = reverse('generationunit-fuel-costs')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 403)