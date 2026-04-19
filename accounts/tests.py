from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from topology.models import Grid, Substation, Feeder, Transformer, Branch
from smart_grid_governor.core.permissions import SovereignPermission, ZoneManagerPermission
from unittest.mock import MagicMock, patch
from django.http import HttpResponse
from accounts.middleware import SovereignAuditMiddleware
from resources.models import FuelType, PowerSource, GenerationUnit
from accounts.services import AccessControlService
from django.contrib.auth.models import AnonymousUser
from economics.models import BillingAcc
from django.contrib.contenttypes.models import ContentType
from tasks.models import Maintenance
from accounts.models import User

class ParentTest(TestCase):
  def setUp(self):
    User = get_user_model()
    self.client = APIClient()
    self.factory = RequestFactory()
    self.zone_a = Grid.objects.create(name = 'zone 1')
    self.zone_b = Grid.objects.create(name = 'zone 2')
    self.admin = User.objects.create_user(username = 'admin', email = 'admingird@gmail.com', control = 'admin')
    self.engineer_a = User.objects.create_user(username = 'eng_a', email = 'eng_agrid@gmail.com', control = 'engineer', zone=self.zone_a)
    self.officer_b = User.objects.create_user(username = 'off_b', email = 'off_bgrid@gmail.com', control = 'officer', zone=self.zone_b)
    self.consumer = User.objects.create_user(username = 'citizen', email = 'citizen@gmail.com', control = 'consumer')

  def auth(self, user):
    self.client.force_authenticate(user=user)
  
  def test_check(self):
    self.assertEqual(self.admin.username, 'admin')
    self.assertEqual(self.engineer_a.username, 'eng_a')
    self.assertEqual(self.officer_b.username, 'off_b')
    self.assertEqual(self.consumer.username, 'citizen')

class PermissionTest(ParentTest):
  def test_sovereign_allows_admin(self):
    request = self.factory.get('/')
    request.user = self.admin
    perm = SovereignPermission()
    self.assertTrue(perm.has_permission(request, None))

  def test_sovereign_blocks_engineer(self):
    request = self.factory.get('/')
    request.user = self.engineer_a
    perm = SovereignPermission()
    self.assertFalse(perm.has_permission(request, None))

  def test_zone_manager_has_perm_authen(self):
    request = self.factory.get('/')
    request.user = self.consumer
    perm = ZoneManagerPermission()
    self.assertTrue(perm.has_permission(request, None))

  def test_zone_manager_blocks_cons_from_object(self):
    request = self.factory.get('/')
    request.user = self.consumer
    perm = ZoneManagerPermission()
    mock_obj = MagicMock() 
    self.assertFalse(perm.has_object_permission(request, None, mock_obj))

  def test_zone_manager_admin_bypass(self):
    request = self.factory.get('/')
    request.user = self.admin
    perm = ZoneManagerPermission()
    mock_obj = MagicMock()
    self.assertTrue(perm.has_object_permission(request, None, mock_obj))

  def test_zone_manager_enforces_zone_bound(self):
    request = self.factory.get('/')
    request.user = self.engineer_a 
    perm = ZoneManagerPermission()
    mock_obj_zone_b = MagicMock()
    mock_obj_zone_b.zone = self.zone_b

    res = perm.has_object_permission(request, None, mock_obj_zone_b)
    self.assertFalse(res, 'the eng a should be blocked from the zone b data')
    
class MiddlewareTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.get_response = MagicMock(return_value=HttpResponse('done'))
    self.middleware = SovereignAuditMiddleware(self.get_response)

  @patch('events.services.EventBus.publish')
  def test_audit_trigger_on_paym_sync(self, mock_publish):
    request = self.factory.post('/economics/economics/sync_payms/', data=[{'amount': 100}], content_type='application/json')
    request.user = self.admin
    self.middleware(request)
    self.assertTrue(mock_publish.called)
    self.assertEqual(mock_publish.call_args[1]['kind'], 'economy')

  @patch('events.services.EventBus.publish')
  def test_audit_trigger_on_meter_reading(self, mock_publish):
    request = self.factory.post('/metering/metering/submit_reading/', data={'reading': 50})
    request.user = self.engineer_a
    self.middleware(request)
    self.assertTrue(mock_publish.called)
    self.assertEqual(mock_publish.call_args[1]['kind'], 'command')

  @patch('events.services.EventBus.publish')
  def test_audit_keyword_classification_theft(self, mock_publish):
    request = self.factory.post('/metering/metering/verify_theft/1/')
    request.user = self.officer_b 
    self.middleware(request)
    self.assertEqual(mock_publish.call_args[1]['kind'], 'theft')

  @patch('events.services.EventBus.publish')
  def test_audit_ignore_safe_get(self, mock_publish):
    request = self.factory.get('/topology/grid/')
    request.user = self.engineer_a 
    self.middleware(request)
    self.assertFalse(mock_publish.called)

  @patch('events.services.EventBus.publish')
  def test_trigger_on_analytics_get(self, mock_publish):
    request = self.factory.get('/analytics/efficiency/')
    request.user = self.admin  
    self.middleware(request)
    self.assertTrue(mock_publish.called)
    self.assertEqual(mock_publish.call_args[1]['kind'], 'economy')
    
class AccessControlServiceTest(TestCase):
  def setUp(self):
    User = get_user_model()
    self.zone_a = Grid.objects.create(name = 'Lahore Central')
    self.zone_b = Grid.objects.create(name = 'Islamabad North')
    self.admin = User.objects.create_superuser(username = 'admin', email = 'admingrid@gmail.com', password = 'admin12312', control = 'admin')
    self.manager_a = User.objects.create_user(username = 'mgr_a', email = 'mgr_agrid@gmail.com', password = 'mgr_a12312', control = 'officer', zone=self.zone_a)
    self.manager_b = User.objects.create_user(username = 'mgr_b', email = 'mgr_bgrid@gmail.com', password = 'mgr_b12312', control = 'officer', zone=self.zone_b)
    self.substation_a = Substation.objects.create(zone=self.zone_a, name = 'Substation A1', max_capa_mw=100.0)
    self.feeder_a = Feeder.objects.create(substation=self.substation_a, code = 'FDR-A1-001')
    self.transformer_a = Transformer.objects.create(feeder=self.feeder_a, uid = 'TRF-A1-X', kva_rating=500)
    self.branch_a = Branch.objects.create(transformer=self.transformer_a, account_number = 'BR-A1-99')
    self.fuel_type = FuelType.objects.create(name = 'Solar', renewable=True)
    self.source_a = PowerSource.objects.create(name = 'Solar Park Alpha', grid_zone=self.zone_a)
    self.gen_unit_a = GenerationUnit.objects.create(source=self.source_a, unit_name = 'Unit 1', installed_capacity_mw=10.0,
      cost_per_unit=5.0, fuel_type=self.fuel_type)

    self.service = AccessControlService()

  def test_admin_full_access(self):
    self.assertTrue(self.service.zone_permission(self.admin, self.branch_a))

  def test_unauthenticated_denial(self):
    anon = AnonymousUser()
    self.assertFalse(self.service.zone_permission(anon, self.zone_a))

  def test_deep_traversal_success(self):
    self.assertTrue(self.service.zone_permission(self.manager_a, self.branch_a))

  def test_cross_zone_denial(self):
    self.assertFalse(self.service.zone_permission(self.manager_b, self.branch_a))

  def test_resource_access(self):
    self.assertTrue(self.service.zone_permission(self.manager_a, self.gen_unit_a))
    self.assertFalse(self.service.zone_permission(self.manager_b, self.gen_unit_a))

  def test_billing_access(self):
    billing_acc = BillingAcc.objects.create(user=self.manager_a, branch=self.branch_a, balance=500.0)
    self.assertTrue(self.service.zone_permission(self.manager_a, billing_acc))

  def test_gfk_maintenance_access(self):
    feeder_type = ContentType.objects.get_for_model(Feeder)   
    maint_task = Maintenance.objects.create(subject = 'Fixing Fuse', content_type=feeder_type, object_id=self.feeder_a.id, 
      status = 'assigned')
    self.assertTrue(self.service.zone_permission(self.manager_a, maint_task))
    self.assertFalse(self.service.zone_permission(self.manager_b, maint_task))

  def test_user_with_no_zone(self):
    lonely_user = User.objects.create_user(username = 'no_zone', email = 'nongrid@gmail.com', password = 'non12312', control = 'officer', zone=None)
    self.assertFalse(self.service.zone_permission(lonely_user, self.substation_a))

  def test_invalid_node_type(self):
    self.assertFalse(self.service.zone_permission(self.manager_a, 'just a grid'))