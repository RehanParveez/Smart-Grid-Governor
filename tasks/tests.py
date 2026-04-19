from accounts.tests import ParentTest
from unittest.mock import MagicMock
from django.http import HttpResponse
from tasks.middleware import MaintenanceMiddleware
from topology.models import Feeder, Substation
from django.contrib.contenttypes.models import ContentType
from tasks.models import Maintenance

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