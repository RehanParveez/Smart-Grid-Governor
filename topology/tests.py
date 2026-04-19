from accounts.tests import ParentTest
from unittest.mock import MagicMock
from django.http import HttpResponse
from topology.middleware import GridLockdownMiddleware
from scheduler.models import Cycle
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from topology.models import Grid, Substation, Feeder, Transformer, Branch
from topology.services import TopologyTreeService
from django.core import mail
from unittest.mock import patch
from topology.tasks import downstream_status
from accounts.models import User

# class LockdownMiddlewareTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.get_response = MagicMock(return_value=HttpResponse('passed'))
#     self.middleware = GridLockdownMiddleware(self.get_response)

#   def test_lockdown_blocks_consumer_on_non_rel_path(self):
#     Cycle.objects.create(zone=self.zone_a, status = 'executing')
#     request = self.factory.post('/economics/payment/') 
#     request.user = self.consumer
#     request.user.zone = self.zone_a 
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 503)
#     self.assertIn('System Lockdown Active', resp.content.decode())

#   def test_lockdown_allows_staff_on_any_path(self):
#     Cycle.objects.create(zone=self.zone_a, status = 'executing')
#     request = self.factory.post('/economics/payment/')
#     request.user = self.engineer_a 
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 200)

#   def test_lockdown_allows_rel_path_for_cons(self):
#     Cycle.objects.create(zone=self.zone_a, status = 'executing')
#     request = self.factory.post('/metering/metering/submit_reading/')
#     request.user = self.consumer
#     request.user.zone = self.zone_a
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 200)

#   def test_no_lockdown_if_no_exec_cycle(self):
#     Cycle.objects.create(zone=self.zone_a, status = 'draft')
#     request = self.factory.post('/economics/payment/')
#     request.user = self.consumer
#     request.user.zone = self.zone_a
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 200)
    
# class TopologyTreeServiceTest(TestCase):
#   def setUp(self):
#     User = get_user_model()
#     cache.clear()
#     self.grid = Grid.objects.create(name = 'Central Lahore')
#     self.sub = Substation.objects.create(zone=self.grid, name = 'Alpha Sub', max_capa_mw=50.0)
#     self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-01', is_energized=True)
#     self.transformer = Transformer.objects.create(feeder=self.feeder, uid = 'TR-X1', kva_rating=250)
#     self.branch = Branch.objects.create(transformer=self.transformer, account_number = 'ACC-100', type = 'industrial')
#     self.admin = User.objects.create_user(username = 'admin', email = 'admin12312', control = 'admin')
#     self.consumer = User.objects.create_user(username = 'consumer', email = 'consumer12312', control = 'consumer')

#     self.service = TopologyTreeService()

#   def test_recursive_struc_success(self):
#     res = self.service.recursive_structure(self.grid.id) 
#     self.assertEqual(res['grid_name'], 'Central Lahore')
#     sub_data = res['substations'][0]
#     self.assertEqual(sub_data['name'], 'Alpha Sub')  
#     feeder_data = sub_data['feeders'][0]
#     self.assertEqual(feeder_data['code'], 'F-01')
#     self.assertEqual(feeder_data['status'], 'ACTIVE') 
#     branch_data = feeder_data['transformers'][0]['branches'][0]
#     self.assertEqual(branch_data['account_number'], 'ACC-100')

#   def test_recursive_struc_caching(self):
#     self.service.recursive_structure(self.grid.id)
#     self.grid.name = 'modified name'
#     self.grid.save()
#     result = self.service.recursive_structure(self.grid.id)
#     self.assertEqual(result['grid_name'], 'Central Lahore')

#   def test_recursive_struc_inv_id(self):
#     self.assertIsNone(self.service.recursive_structure(9999))

#   def test_feeder_power_toggle(self):
#     updated_feeder = self.service.feeder_power(self.feeder, self.admin)
#     self.assertFalse(updated_feeder.is_energized)
#     self.assertTrue(updated_feeder.is_shedding_active)
#     final_feeder = self.service.feeder_power(updated_feeder, self.admin)
#     self.assertTrue(final_feeder.is_energized)
#     self.assertFalse(final_feeder.is_shedding_active)

#   def test_feeder_power_perm_denied(self):
#     result = self.service.feeder_power(self.feeder, self.consumer)
#     self.assertIsNone(result)
#     self.feeder.refresh_from_db()
#     self.assertTrue(self.feeder.is_energized)

#   def test_branch_children_logic(self):
#     feeders = self.service.branch_children('substation', self.sub.id)
#     self.assertIn(self.feeder, feeders)
#     transformers = self.service.branch_children('feeder', self.feeder.id)
#     self.assertIn(self.transformer, transformers)
#     branches = self.service.branch_children('transformer', self.transformer.id)
#     self.assertIn(self.branch, branches)

#   def test_branch_children_inv_type(self):
#     res = self.service.branch_children('invalid_type', 1)
#     self.assertEqual(list(res), [])
    
class TopologyIntegrationTest(TestCase):
  def setUp(self):
    cache.clear()
    self.grid = Grid.objects.create(name = 'Lahore West')
    self.sub = Substation.objects.create(zone=self.grid, name = 'Substation 5', max_capa_mw=80)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'FDR-TEST', is_energized=True)
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'TR-909', kva_rating=200)
    self.branch = Branch.objects.create(transformer=self.trans, account_number = 'BR-CHECK-01')
    self.consumer = User.objects.create_user(username = 'consumer test', email ='consumer@gmail.com', control = 'consumer', zone=self.grid)

  @patch('topology.signals.downstream_status.delay')
  def test_signal_trigg_celery(self, mock_delay):
    self.feeder.is_energized = False
    self.feeder.save()
    mock_delay.assert_called_once_with(self.feeder.id, False)

  def test_task_upd_downstream_status(self):
    downstream_status(self.feeder.id, False)
    self.trans.refresh_from_db()
    self.branch.refresh_from_db()
    self.assertFalse(self.trans.is_energized)
    self.assertFalse(self.branch.is_energized)

  def test_task_sends_email_to_corr_users(self):
    downstream_status(self.feeder.id, True)
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].subject, 'Electricity PowerRESTORED')
    self.assertIn('consumer@gmail.com', mail.outbox[0].to)
        
  def test_cache_is_del_on_feeder_chan(self):
    tree_key = f'zone {self.grid.id} tree'
    cache.set(tree_key, {'old': 'data'})
    self.feeder.save()
    self.assertIsNone(cache.get(tree_key))