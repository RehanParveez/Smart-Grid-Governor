from accounts.tests import ParentTest
from topology.models import Substation, Feeder, Transformer, Branch, Grid
from economics.models import BillingAcc, FeedFinanHealth
from events.services import EventBus
from events.models import AuditRecord
from notifications.models import Alert
from unittest.mock import patch
from django.contrib.contenttypes.models import ContentType 
from django.urls import reverse

class EventBusTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub-Event', max_capa_mw=130)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-EVENT')
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'TR-EVENT', kva_rating=560)
    self.branch = Branch.objects.create(transformer=self.trans, account_number = 'ACC-EV-01')
    self.consumer.zone = self.zone_a
    self.consumer.save()
    self.bill_acc = BillingAcc.objects.create(user=self.consumer, branch=self.branch)
    self.health = FeedFinanHealth.objects.create(feeder=self.feeder, reco_percent=30)

  def test_publish_creates_audit_rec(self):
    payload = {'action': 'manual_override', 'reason': 'maintenance'}
    event = EventBus.publish(kind = 'command', zone=self.zone_a, actor=self.admin, target=self.sub, payload=payload)
    self.assertEqual(AuditRecord.objects.count(), 1)
    self.assertEqual(event.action, 'manual_override')
    self.assertEqual(event.kind, 'command')
    self.assertEqual(event.user, self.admin)

  @patch('notifications.tasks.alert_delivery.delay')
  def test_publish_stress_trigg_notifi(self, mock_celery):
    payload = {'action': 'load_shed_imminent', 'recovery': 35}
    EventBus.publish(kind = 'stress', zone=self.zone_a, actor=None, target=None, payload=payload)
    self.assertTrue(AuditRecord.objects.filter(kind='stress').exists())
    alert = Alert.objects.filter(user=self.consumer).first()
    self.assertIsNotNone(alert)
    self.assertIn('pay the bills', alert.message)
    mock_celery.assert_called_once_with(alert.id)

  def test_publish_without_action_in_pay(self):
    event = EventBus.publish(kind = 'work', zone=self.zone_a, actor=self.engineer_a, target=self.branch, 
      payload={'notes': 'repaired line'})
    self.assertEqual(event.action, 'auto_system')

class EventViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub A', max_capa_mw=190.0)
    self.feeder = Feeder.objects.create(substation=self.sub, code ='F-1')
    self.trans = Transformer.objects.create(feeder=self.feeder, uid = 'TR-1', kva_rating=600)
    self.ct_trans = ContentType.objects.get_for_model(Transformer)
    self.rec_direct = AuditRecord.objects.create(kind = 'work', zone=self.zone_a, action = 'maintenance', user=self.engineer_a)
    self.rec_gfk = AuditRecord.objects.create(kind = 'stress', content_type=self.ct_trans, object_id=self.trans.id, 
      action = 'high_load', user=None)
    self.sec_zone = Grid.objects.create(name = 'Sec Zone')
    self.rec_sec = AuditRecord.objects.create(kind = 'work', zone=self.sec_zone, action = 'rogue_action')
    self.list_url = reverse('event-list')
    self.stream_url = reverse('event-stream')

  def test_admin_access_all_events(self):
    self.auth(self.admin)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 3)

  def test_engineer_access_denied_on_list(self):
    self.auth(self.engineer_a)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 403)

  def test_stream_zone_filter(self):
    self.auth(self.engineer_a)
    resp = self.client.get(self.stream_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['kind'], 'stress')

  def test_stream_order_and_limit(self):
    self.auth(self.admin)
    resp = self.client.get(self.stream_url)
    for item in resp.data:
      self.assertIn(item['kind'], ['stress', 'theft'])
