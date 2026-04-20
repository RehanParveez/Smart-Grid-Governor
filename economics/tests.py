from accounts.tests import ParentTest
from unittest.mock import MagicMock
from django.http import HttpResponse
from economics.middleware import EconomicsRoleMiddleware
from topology.models import Substation, Feeder, Transformer, Branch
from economics.models import BillingAcc, PaymentRec
from decimal import Decimal
from economics.services import RevenueAnalyService
from django.core.cache import cache
from accounts.models import User
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

# class EconomicsMiddlewareTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.get_response = MagicMock(return_value=HttpResponse('passed', status=200))
#     self.middleware = EconomicsRoleMiddleware(self.get_response)

#   def test_unauthenticated_user_blocked(self):
#     request = self.factory.get('/economics/economics/top_perfs/')
#     request.user = MagicMock(is_authenticated=False) 
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 401)

#   def test_consumer_blocked_from_economics(self):
#     request = self.factory.get('/economics/economics/feeder/health/')
#     request.user = self.consumer 
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 403)
#     self.assertIn('the consu cant view data', resp.content.decode())

#   def test_consumer_blocked_from_prioriti(self):
#     request = self.factory.get('/prioritization/priority/')
#     request.user = self.consumer  
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 403)

#   def test_admin_allowed_on_restric_keyw(self):
#     request = self.factory.get('/prioritization/priority/factors/')
#     request.user = self.admin  
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 200)
#     self.assertEqual(resp.content.decode(), 'passed')

#   def test_engineer_allowed_on_recalculate(self):
#     request = self.factory.post('/prioritization/priority/recalculate/')
#     request.user = self.engineer_a  
#     resp = self.middleware(request)
#     self.assertEqual(resp.status_code, 200)
    
# class RevenueAnalyServiceTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=100)
#     self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-101', curr_load_mw=Decimal('10.00'))
#     self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'T-1', kva_rating=500)
#     self.branch_1 = Branch.objects.create(transformer=self.trans, account_number = 'ACC-01')
#     self.branch_2 = Branch.objects.create(transformer=self.trans, account_number = 'ACC-02')
#     self.acc_1 = BillingAcc.objects.create(user=self.consumer, branch=self.branch_1)
#     self.acc_2 = BillingAcc.objects.create(user=self.consumer, branch=self.branch_2)

#   def test_reve_calc_logic(self):
#     PaymentRec.objects.create(account=self.acc_1, amount_paid=Decimal('500.00'), reference_id = 'REF1')
#     PaymentRec.objects.create(account=self.acc_2, amount_paid=Decimal('250.00'), reference_id = 'REF2')
#     health = RevenueAnalyService.calc_feeder(self.feeder)
#     self.assertEqual(health.reco_percent, Decimal('50.00'))
#     self.assertEqual(health.tot_defecit, Decimal('750.00'))
#     cache_key = f'feeder {self.feeder.id} reco_perf'
#     self.assertEqual(cache.get(cache_key), 50.0)

#   def test_zero_load_handl(self):
#     self.feeder.curr_load_mw = Decimal('0.00')
#     self.feeder.save()
#     health = RevenueAnalyService.calc_feeder(self.feeder)
#     self.assertEqual(health.reco_percent, Decimal('0.00'))
#     self.assertEqual(health.tot_defecit, Decimal('0.00'))

#   def test_no_payms_handling(self):
#     health = RevenueAnalyService.calc_feeder(self.feeder)
#     self.assertEqual(health.reco_percent, Decimal('0.00'))
#     self.assertEqual(health.tot_defecit, Decimal('1500.00'))
    
# class EconomicsSignalTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.sub = Substation.objects.create(zone=self.zone_a, name = 'Substation', max_capa_mw=50)
#     self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-SIGNAL')
#     self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'T-SIGNAL', kva_rating=200)

#   def test_bill_acc_created_when_user_matches(self):
#     acc_num = 'CONSUMER-99'
#     User.objects.create_user(username=acc_num, email = 'user3@gmail.com', password = 'user112312', control = 'consumer')
#     branch = Branch.objects.create(transformer=self.trans, account_number=acc_num, type = 'residential')
#     bill_exists = BillingAcc.objects.filter(branch=branch, user__username=acc_num)
#     bill_exists = bill_exists.exists()
#     self.assertTrue(bill_exists)
#     acc = BillingAcc.objects.get(branch=branch)
#     self.assertEqual(acc.balance, Decimal('0.00'))

#   def test_no_bill_acc_when_user_missing(self):
#     acc_num = 'UNKNOWN-023'
#     branch = Branch.objects.create(transformer=self.trans, account_number=acc_num)
#     bill_exists = BillingAcc.objects.filter(branch=branch)
#     bill_exists = bill_exists.exists()
#     self.assertFalse(bill_exists)

#   def test_sign_only_runs_on_crea(self):
#     acc_num = 'CONSUMER-150'
#     _ = User.objects.create_user(username=acc_num, email = 'c150@gmail.com', password = 'c15012312')
#     branch = Branch.objects.create(transformer=self.trans, account_number=acc_num)
#     self.assertEqual(BillingAcc.objects.filter(branch=branch).count(), 1)
#     branch.is_energized = False
#     branch.save()
#     self.assertEqual(BillingAcc.objects.filter(branch=branch).count(), 1)

class EconomicsViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    acc_num = 'FB-ACC-01'
    self.billing_user = User.objects.create_user(username=acc_num, email = 'fb_owner@gmail.com', password = 'fb_owner12312')
    self.engineer_b = User.objects.create_user(username = 'eng_b_economics', email = 'eng_b@gmail.com', password = 'eng_b12312',
      control = 'engineer', zone=self.zone_b)
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub-X', max_capa_mw=100)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-05', curr_load_mw=Decimal('10.00'))
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'T-TD', kva_rating=500)
    self.branch = Branch.objects.create(transformer=self.trans, account_number = 'FB-ACC-01')
    self.bill_acc = BillingAcc.objects.get(branch=self.branch)

  def test_sync_payms_bulk_upl(self):
    refresh = RefreshToken.for_user(self.admin)
    token = str(refresh.access_token)
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('economics-sync-payms')
    data = [{'account': self.bill_acc.id, 'amount_paid': '500.00', 'reference_id': 'PAY-001'},
      {'account': self.bill_acc.id, 'amount_paid': '300.00', 'reference_id': 'PAY-002'}]
    resp = self.client.post(url, data, format = 'json')
    self.assertEqual(resp.status_code, 201)
    self.assertEqual(resp.data['count'], 2)
    self.assertEqual(PaymentRec.objects.count(), 2)

  def test_feeder_health_calc(self):
    refresh = RefreshToken.for_user(self.engineer_a)
    token = str(refresh.access_token)
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    PaymentRec.objects.create(account=self.bill_acc, amount_paid=Decimal('1500.00'), reference_id = 'REF-HEALTH')
    url = reverse('economics-feeder-health', kwargs={'feeder_id': self.feeder.id})
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(Decimal(resp.data['reco_percent']), Decimal('100.00'))

  def test_zone_isola_on_payms(self):
    PaymentRec.objects.create(account=self.bill_acc, amount_paid=Decimal('100.00'), reference_id = 'PAY-ZONE-A')
    refresh = RefreshToken.for_user(self.engineer_b)
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    url = reverse('payment-list')
    resp = self.client.get(url)
    self.assertEqual(len(resp.data), 0)