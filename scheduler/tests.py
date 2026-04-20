from accounts.tests import ParentTest
from scheduler.models import SheddingTarget, Cycle
from django.utils import timezone
from topology.models import Substation, Feeder, Transformer, Branch
from prioritization.models import FeedPriorScore
from scheduler.services import LoadSheddingOptimizer
from unittest.mock import patch
from django.urls import reverse

# class SchedulerServiceTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=15.0, start_time=timezone.now(), expec_dura_mins=50)
#     self.cycle = Cycle.objects.create(zone=self.zone_a, target=self.target, status = 'draft')
#     self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub 1', max_capa_mw=100)
#     self.f1 = Feeder.objects.create(substation=self.sub, code = 'F1', curr_load_mw=10.0)
#     FeedPriorScore.objects.create(feeder=self.f1, rank_in_zone=10, final_score=20.0)
#     self.f2 = Feeder.objects.create(substation=self.sub, code = 'F2', curr_load_mw=10.0)
#     FeedPriorScore.objects.create(feeder=self.f2, rank_in_zone=9, final_score=30.0)

#   def test_optim_logic_picks_corr_feeders(self):
#     optimizer = LoadSheddingOptimizer()
#     plans = optimizer.optim_plan(self.cycle)
#     self.cycle.refresh_from_db()
#     self.assertEqual(len(plans), 2)
#     self.assertEqual(float(self.cycle.total_mw_saved), 20.0)

#   def test_criti_infrastr_bypass(self):
#     tr = Transformer.objects.create(feeder=self.f1, uid = 'TR1', kva_rating=140)
#     Branch.objects.create(transformer=tr, account_number = 'B1', type = 'important')
#     optimizer = LoadSheddingOptimizer()
#     plans = optimizer.optim_plan(self.cycle)
#     self.assertEqual(len(plans), 1)
#     self.assertEqual(plans[0].feeder, self.f2)
    
# class CycleSignalTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=10.0, start_time=timezone.now(), expec_dura_mins=30)
#     self.cycle = Cycle.objects.create(zone=self.zone_a, target=self.target, status = 'draft')

#   @patch('scheduler.tasks.dispa_commands.delay')
#   def test_signal_triggers_on_approved(self, mock_task):
#     self.cycle.status = 'approved'
#     self.cycle.save()
#     mock_task.assert_called_once_with(self.cycle.id)

#   @patch('scheduler.tasks.dispa_commands.delay')
#   def test_signal_doesnt_trig_on_other_status(self, mock_task):
#     self.cycle.status = 'cancelled'
#     self.cycle.save()
#     mock_task.assert_not_called()

#   @patch('scheduler.tasks.dispa_commands.delay')
#   def test_signal_does_not_trigger_on_creation(self, mock_task):
#     sec_target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=5.0, start_time=timezone.now(), 
#       expec_dura_mins=20)
#     Cycle.objects.create(zone=self.zone_a, target=sec_target, status = 'approved')
#     mock_task.assert_not_called()
    
class SchedulerViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=10.0, start_time=timezone.now(), expec_dura_mins=30)
    self.load_shed_url = reverse('cycle-load-shed')

  def test_load_shed_creates_cycle(self):
    self.auth(self.engineer_a)
    payload = {'target_id': self.target.id}
    resp = self.client.post(self.load_shed_url, payload, format = 'json')
    self.assertEqual(resp.status_code, 201)
    self.assertEqual(Cycle.objects.filter(zone=self.zone_a).count(), 1)
    self.assertEqual(resp.data['status'], 'draft')

  def test_load_shed_notallowed_for_wrong_zone(self):
    self.auth(self.officer_b)
    payload = {'target_id': self.target.id}
    resp = self.client.post(self.load_shed_url, payload, format = 'json')
    self.assertEqual(resp.status_code, 403)
    self.assertEqual(resp.data['err'], 'no acc is allow. to this zone')

  @patch('events.services.EventBus.publish')
  def test_approve_cycle_as_mana(self, mock_publish):
    cycle = Cycle.objects.create(target=self.target, zone=self.zone_a, status = 'draft')
    self.auth(self.engineer_a)
    approve_url = reverse('cycle-approve', kwargs={'pk': cycle.id})
    resp = self.client.post(approve_url)
    cycle.refresh_from_db()
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(cycle.status, 'approved')
    mock_publish.assert_any_call(kind = 'stress', zone=self.zone_a, actor=self.engineer_a, target=cycle, 
      payload={'recovery': 30, 'action': 'cycle_approval'})

  def test_active_cycles_filter(self):
    Cycle.objects.create(target=self.target, zone=self.zone_a, status = 'draft')
    t2 = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=5, start_time=timezone.now(),
      expec_dura_mins=10)
    Cycle.objects.create(target=t2, zone=self.zone_a, status = 'approved')
    self.auth(self.engineer_a)
    active_url = reverse('cycle-active-cycles')
    resp = self.client.get(active_url)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['status'], 'approved')