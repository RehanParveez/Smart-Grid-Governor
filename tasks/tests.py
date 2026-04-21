from accounts.tests import ParentTest
from unittest.mock import MagicMock
from django.http import HttpResponse
from tasks.middleware import MaintenanceMiddleware
from topology.models import Feeder, Substation, Transformer, Branch, Grid
from django.contrib.contenttypes.models import ContentType
from tasks.models import Maintenance, Investigation
from responders.models import Capability, Team
from metering.models import LossAbnormality
from tasks.services import ShipService
from django.core.cache import cache
from django.urls import reverse

class MaintenanceMiddlewareTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.get_response = MagicMock(return_value=HttpResponse('passed', status=200))
    self.middleware = MaintenanceMiddleware(self.get_response)
    self.test_substation = Substation.objects.create(zone=self.zone_a, name = 'substation test', max_capa_mw=100.0)
    self.test_feeder = Feeder.objects.create(substation=self.test_substation, code='R-UNIT-TEST', curr_load_mw=0.0)
    self.feeder_type = ContentType.objects.get_for_model(Feeder)
   
  def test_block_exec_callback_dur_ongoing_mainte(self):
    Maintenance.objects.create(subject = 'the feeder repair', content_type=self.feeder_type, object_id=self.test_feeder.id,
      status = 'ongoing')
    request = self.factory.post('/execution/hardware_callback/', data={'feeder_id': self.test_feeder.id})
    request.user = self.engineer_a
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 403)
    self.assertIn('the maintenance is ongoing', resp.content.decode())

  def test_allow_execu_when_mainte_is_solved(self):
    Maintenance.objects.create(subject = 'task is comple', content_type=self.feeder_type, object_id=self.test_feeder.id,
      status = 'solved')
    request = self.factory.post('/execution/hardware_callback/', data={'feeder_id': self.test_feeder.id})
    request.user = self.engineer_a
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content.decode(), 'passed')

  def test_allow_execu_if_no_mainte_rec_exists(self):
    request = self.factory.post('/execution/hardware_callback/', data={'feeder_id': self.test_feeder.id})
    request.user = self.engineer_a
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 200)

  def test_middleware_ignores_non_execu_paths(self):
    Maintenance.objects.create(subject = 'dangerous work', content_type=self.feeder_type,
      object_id=self.test_feeder.id, status = 'ongoing')
    request = self.factory.post('/analytics/efficiency/', data={'feeder_id': self.test_feeder.id})
    request.user = self.admin
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 200)
    
class ShipServiceTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Main Sub', max_capa_mw=160.0)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-01')
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'T-77', kva_rating=260)
    self.branch = Branch.objects.create(transformer=self.trans, account_number = 'ACC-105')
    self.team = Team.objects.create(name = 'Anti-Theft Unit', zone=self.zone_a, is_active=True)
    Capability.objects.create(team=self.team, skill = 'theft')

  def test_assign_theft_inv_done_for_branch(self):
    branch_type = ContentType.objects.get_for_model(self.branch)
    abnorm = LossAbnormality.objects.create(content_type=branch_type, object_id=self.branch.id, loss_percentage=85.5,
      severity = 'high')
    task = Maintenance.objects.filter(assigned=self.team)
    task = task.first()
    self.assertIsNotNone(task)
    self.assertEqual(task.subject, '85.5% loss')
    inv = Investigation.objects.filter(abnorma=abnorm)
    inv = inv.first()
    self.assertIsNotNone(inv)
    self.assertEqual(inv.task, task)
    self.assertTrue(cache.get('GRID_LOCKDOWN_ENABLED'))

  def test_assign_theft_inv_fails_when_no_team(self):
    self.team.is_active = False
    self.team.save()
    branch_kind = ContentType.objects.get_for_model(self.branch)
    abnorm = LossAbnormality.objects.create(content_type=branch_kind, object_id=self.branch.id, loss_percentage=50.0)
    res = ShipService.assign_theft_inv(abnorm)
    self.assertEqual(res, f'no team avail. in {self.zone_a.name}')

  def test_zone_passing(self):
    feeder_kind = ContentType.objects.get_for_model(self.feeder)
    abnorm = LossAbnormality.objects.create(content_type=feeder_kind, object_id=self.feeder.id, loss_percentage=40.0)
    res = ShipService.assign_theft_inv(abnorm)
    self.assertEqual(res, f'{self.team.name} is shipped')
    
class TaskViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub_a = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=80.0)
    self.feeder_a = Feeder.objects.create(substation=self.sub_a, code = 'F-A')
    self.fdr_ct = ContentType.objects.get_for_model(Feeder)
    self.team_a = Team.objects.create(name = 'A Team', zone=self.zone_a)
    self.team_a.members.add(self.engineer_a)
    self.task_a = Maintenance.objects.create(subject = 'Fix Feeder A', content_type=self.fdr_ct, object_id=self.feeder_a.id,
      assigned=self.team_a, status = 'assigned')

    self.zone_b = Grid.objects.create(name = 'Zone B')
    self.sub_b = Substation.objects.create(zone=self.zone_b, name = 'Sub B', max_capa_mw=60.0)
    self.feeder_b = Feeder.objects.create(substation=self.sub_b, code = 'F-B')
    self.task_b = Maintenance.objects.create(
      subject = 'Fix Feeder B', content_type=self.fdr_ct, object_id=self.feeder_b.id, status = 'assigned')
    self.list_url = reverse('task-list')

  def test_get_queryset_gfk_filtering(self):
    self.auth(self.engineer_a)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['subject'], 'Fix Feeder A')

  def test_my_tasks(self):
    url = reverse('task-my-tasks')
    self.auth(self.engineer_a)
    self.task_a.status = 'ongoing'
    self.task_a.save()
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['subject'], 'Fix Feeder A')

  def test_update_status(self):
    url = reverse('task-update-status', kwargs={'pk': self.task_a.pk})
    self.auth(self.engineer_a)
    data = {'status': 'ongoing'}
    resp = self.client.patch(url, data)
    self.assertEqual(resp.status_code, 200)
    self.task_a.refresh_from_db()
    self.assertEqual(self.task_a.status, 'ongoing')

  def test_upd_status_inv_choice(self):
    url = reverse('task-update-status', kwargs={'pk': self.task_a.pk})
    self.auth(self.engineer_a)
    data = {'status': 'no_status'}
    resp = self.client.patch(url, data)
    self.assertEqual(resp.status_code, 400)
    self.assertIn('err', resp.data)