from accounts.tests import ParentTest
from topology.models import Substation, Feeder, Transformer, Branch
from economics.models import BillingAcc, FeedFinanHealth
from notifications.services import PublicTransparency
from notifications.models import Alert
from unittest.mock import patch
from topology.models import Grid
from accounts.models import User
from django.urls import reverse

class PublicTransparencyTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=180)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-99')
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'TR-99', kva_rating=650)
    self.branch = Branch.objects.create(transformer=self.trans, account_number = 'ACC-ALRT-023')
    self.bill_acc = BillingAcc.objects.create(user=self.consumer, branch=self.branch)
    self.health = FeedFinanHealth.objects.create(feeder=self.feeder, reco_percent=35)

  @patch('notifications.tasks.alert_delivery.delay')
  def test_grid_warning_low_recov_msg(self, mock_celery):
    payload = {'recovery': 55} 
    PublicTransparency.grid_warning(self.zone_a, payload)
    alert = Alert.objects.filter(user=self.consumer)
    alert = alert.first()
    self.assertIsNotNone(alert)
    self.assertEqual(alert.kind, 'warning')
    expected_msg = f'{self.zone_a.name} recovery is 55% pay the bills to avoid load shedding'
    self.assertEqual(alert.message, expected_msg[:70])
    mock_celery.assert_called_once_with(alert.id)

  @patch('notifications.tasks.alert_delivery.delay')
  def test_grid_warning_high_recov_msg(self, mock_celery):
    self.health.reco_percent = 80
    self.health.save()
    payload = {'recovery': 90}
    PublicTransparency.grid_warning(self.zone_a, payload)
    alert = Alert.objects.filter(user=self.consumer)
    alert = alert.first()
    expected_msg = f'{self.zone_a.name} recovery is 90%'
    self.assertEqual(alert.message, expected_msg)
    self.assertNotIn('pay the bills', alert.message)
    mock_celery.assert_called_once_with(alert.id)

  def test_grid_warning_no_zone(self):
    res = PublicTransparency.grid_warning(None, {})
    self.assertIsNone(res)
    self.assertEqual(Alert.objects.count(), 0)
    
class NotificationViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.consumer.zone = self.zone_a
    self.consumer.save()
    self.sub_a = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=140)
    self.feeder_a = Feeder.objects.create(substation=self.sub_a, code = 'F-A')
    self.trans_a = Transformer.objects.create(feeder=self.feeder_a, uid = 'TR-A', kva_rating=550)
    self.branch_a = Branch.objects.create(transformer=self.trans_a, account_number = 'ACC-A')
    self.acc_a = BillingAcc.objects.create(user=self.consumer, branch=self.branch_a)
    self.zone_b = Grid.objects.create(name = 'Zone B')
    self.sub_b = Substation.objects.create(zone=self.zone_b, name = 'Sub B', max_capa_mw=160)
    self.feeder_b = Feeder.objects.create(substation=self.sub_b, code = 'F-B')
    self.trans_b = Transformer.objects.create(feeder=self.feeder_b, uid = 'TR-B', kva_rating=580)
    self.branch_b = Branch.objects.create(transformer=self.trans_b, account_number = 'ACC-B')
    self.consumer_b = User.objects.create_user(username = 'citizen_a', email = 'cit@gmail.com', password = 'cit12312', control = 'consumer', zone=self.zone_b)
    self.acc_b = BillingAcc.objects.create(user=self.consumer_b, branch=self.branch_b)
    self.alert_a = Alert.objects.create(user=self.consumer, account=self.acc_a, kind = 'warning', message = 'Zone A Alert')
    self.alert_b = Alert.objects.create(user=self.consumer_b, account=self.acc_b, kind = 'warning', message = 'Zone B Alert')
    self.list_url = reverse('notification-list')
    self.outbox_url = reverse('notification-outbox')

  def test_consumer_access_isola(self):
    self.auth(self.consumer)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['message'], 'Zone A Alert')

  def test_engineer_zone_access(self):
    self.auth(self.engineer_a)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['message'], 'Zone A Alert')

  def test_admin_full_access(self):
    self.auth(self.admin) 
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 2)

  def test_outbox_order(self):
    self.auth(self.admin)
    resp = self.client.get(self.outbox_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.data[0]['message'], 'Zone B Alert')
