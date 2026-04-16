from execution.models import GridWork, HardwareFeedback
from django.contrib.contenttypes.models import ContentType
from metering.models import LossAbnormality

class GridCommandOperator:
  def send_command(self, work_id):
    work = GridWork.objects.filter(pk=work_id)
    work = work.first()
    if not work:
      return 'err: the work is missing'
    work.status = 'sent'
    work.save()
    return 'command_operated'

class VerificationService:
  def verify_work(self, feedback_id):
    feedback = HardwareFeedback.objects.filter(pk=feedback_id)
    feedback = feedback.first()
    work = feedback.work
    feeder = work.feeder
        
    if work.work_kind == 'shed':
      if feedback.load_at_feedback > 0.5:
        feeder_type = ContentType.objects.get_for_model(feeder)
        LossAbnormality.objects.create(content_type=feeder_type, object_id=feeder.id, loss_percentage=100.00, severity = 'high', is_verified=False)
            
        msg = 'feeder ' + str(feeder.code)
        msg = msg + ' failure, the bypass of hardware is detec.'
        print(msg)
                
        return 'tamper_detected'
    return 'verification_done'