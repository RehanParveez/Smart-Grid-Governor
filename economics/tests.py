from accounts.tests import ParentTest
from unittest.mock import MagicMock
from django.http import HttpResponse
from economics.middleware import EconomicsRoleMiddleware

class EconomicsMiddlewareTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.get_response = MagicMock(return_value=HttpResponse('passed', status=200))
    self.middleware = EconomicsRoleMiddleware(self.get_response)

  def test_unauthenticated_user_blocked(self):
    request = self.factory.get('/economics/economics/top_perfs/')
    request.user = MagicMock(is_authenticated=False) 
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 401)

  def test_consumer_blocked_from_economics(self):
    request = self.factory.get('/economics/economics/feeder/health/')
    request.user = self.consumer 
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 403)
    self.assertIn('the consu cant view data', resp.content.decode())

  def test_consumer_blocked_from_prioriti(self):
    request = self.factory.get('/prioritization/priority/')
    request.user = self.consumer  
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 403)

  def test_admin_allowed_on_restric_keyw(self):
    request = self.factory.get('/prioritization/priority/factors/')
    request.user = self.admin  
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content.decode(), 'passed')

  def test_engineer_allowed_on_recalculate(self):
    request = self.factory.post('/prioritization/priority/recalculate/')
    request.user = self.engineer_a  
    resp = self.middleware(request)
    self.assertEqual(resp.status_code, 200)