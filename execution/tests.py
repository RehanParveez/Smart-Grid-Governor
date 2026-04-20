from accounts.tests import ParentTest
from scheduler.models import SheddingTarget, Cycle, LoadBalPlan
from django.utils import timezone
from topology.models import Substation, Feeder
from execution.models import GridWork, HardwareFeedback
from execution.services import GridCommandOperator, VerificationService
from metering.models import LossAbnormality
from django.urls import reverse

# class ExecutionServiceTest(ParentTest):
#   def setUp(self):
#     super().setUp()
#     self.target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=10.0, start_time=timezone.now(), expec_dura_mins=35)
#     self.cycle = Cycle.objects.create(target=self.target, zone=self.zone_a, status = 'approved')
#     self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub 4', max_capa_mw=170.0)
#     self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-EXEC', curr_load_mw=10.0)
#     self.plan = LoadBalPlan.objects.create(cycle=self.cycle, feeder=self.feeder, prior_at_exec=20.0, 
#       rank_at_exec=1, planned_off_time=timezone.now(), planned_on_time=timezone.now() + timezone.timedelta(minutes=35))

#   def test_grid_command_oper_sent_status(self):
#     work = GridWork.objects.create(plan=self.plan, feeder=self.feeder, work_kind = 'shed')
#     operator = GridCommandOperator()
#     result = operator.send_command(work.id)
#     work.refresh_from_db()
#     self.assertEqual(result, 'command_operated')
#     self.assertEqual(work.status, 'sent')

#   def test_verifi_detects_fraud(self):
#     work = GridWork.objects.create(plan=self.plan, feeder=self.feeder, work_kind = 'shed', status = 'sent')
#     feedback = HardwareFeedback.objects.create(work=work, response_payload={'status':'ok'}, delay_ms=120, load_at_feedback=5.0)
#     verifier = VerificationService()
#     res = verifier.verify_work(feedback.id)
#     self.assertEqual(res, 'tamper_detected')
#     abnorma = LossAbnormality.objects.filter(object_id=self.feeder.id)
#     abnorma = abnorma.first()
#     self.assertIsNotNone(abnorma)
#     self.assertEqual(abnorma.severity, 'high')
#     self.assertEqual(float(abnorma.loss_percentage), 100.0)

#   def test_verifi_done(self):
#     work = GridWork.objects.create(plan=self.plan, feeder=self.feeder, work_kind = 'shed')
#     feedback = HardwareFeedback.objects.create(work=work, response_payload={'status': 'ok'}, 
#       delay_ms=100, load_at_feedback=0.1)
#     verifier = VerificationService()
#     res = verifier.verify_work(feedback.id)
#     self.assertEqual(res, 'verification_done')
#     self.assertFalse(LossAbnormality.objects.filter(object_id=self.feeder.id).exists())
    
class ExecutionViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub 7', max_capa_mw=100.0)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-06', curr_load_mw=10.0, is_energized=True)
    self.target = SheddingTarget.objects.create(zone=self.zone_a, needed_red_mw=10.0, start_time=timezone.now(),
      expec_dura_mins=30)
    self.cycle = Cycle.objects.create(target=self.target, zone=self.zone_a, status = 'approved')
    self.plan = LoadBalPlan.objects.create(cycle=self.cycle, feeder=self.feeder, prior_at_exec=20.0, rank_at_exec=1, planned_off_time=timezone.now(), 
      planned_on_time=timezone.now() + timezone.timedelta(minutes=30))
    self.work = GridWork.objects.create(plan=self.plan, feeder=self.feeder, work_kind = 'shed', status = 'sent')
    self.callback_url = reverse('execution-hardware-callback')
    self.pending_url = reverse('execution-pending')

  def test_hardware_callback_shed_done(self):
    self.auth(self.engineer_a)
    payload = {'work_id': self.work.id, 'current_load': 0.1, 'delay_ms': 150}
    resp = self.client.post(self.callback_url, payload, format = 'json')
    self.work.refresh_from_db()
    self.feeder.refresh_from_db()
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(self.work.status, 'confirmed')
    self.assertFalse(self.feeder.is_energized) 
    self.assertEqual(HardwareFeedback.objects.filter(work=self.work).count(), 1)

  def test_hardware_callback_rest_done(self):
    self.feeder.is_energized = False
    self.feeder.save()
    restore_work = GridWork.objects.create(plan=self.plan, feeder=self.feeder, work_kind = 'restore', status = 'sent')
    self.auth(self.engineer_a)
    payload = {'work_id': restore_work.id, 'current_load': 8.5, 'delay_ms': 130}
    self.client.post(self.callback_url, payload, format = 'json')
    self.feeder.refresh_from_db()
    self.assertTrue(self.feeder.is_energized)

  def test_pend_work_filter(self):
    self.auth(self.engineer_a)
    resp = self.client.get(self.pending_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['work_kind'], self.work.work_kind)

  def test_cons_cant_access_exec(self):
    self.auth(self.consumer)
    resp = self.client.get(self.pending_url)
    self.assertEqual(resp.status_code, 403)
