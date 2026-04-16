from celery import shared_task
from scheduler.models import Cycle, SheddingTarget
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from resources.models import GenerationUnit
from django.db.models import Sum
from topology.models import Feeder, Grid
from execution.models import GridWork
from execution.services import GridCommandOperator

@shared_task
def dispa_commands(cycle_id):
  cycle = Cycle.objects.filter(pk=cycle_id)
  cycle = cycle.first()
  if not cycle:
    return 'err: the cycle is not pres.'

  plans = cycle.plans.all()
  feeder_codes = ""
  for plan in plans:
    f = plan.feeder
    work_record = GridWork.objects.create(plan=plan, feeder=f, work_kind = 'shed', status = 'sent')
    opera = GridCommandOperator()
    opera.send_command(work_record.id)
        
    plan.is_executed = True
    plan.executed_at = timezone.now()
    plan.save()
    feeder_codes = feeder_codes + " " + f.code

  cycle.status = 'executing'
  cycle.save()

  subject = 'koad shedding execu'
  line1 = 'the autom. load shedd. is star.'
  line2 = 'cycle id: ' + str(cycle.id)
  line3 = 'zone: ' + str(cycle.zone.name)
  line4 = 'feeders: ' + feeder_codes
    
  full_message = line1 + " " + line2 + " " + line3 + " " + line4

  send_mail(subject, full_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER],
    fail_silently=False)
    
  return 'the commands dispatched'

@shared_task
def min_grid_load():
  supply_query = GenerationUnit.objects.filter(operational=True).aggregate(Sum('curr_output_mw'))
  supply = supply_query['curr_output_mw__sum']
  if supply == None:
        supply = 0

  demand_query = Feeder.objects.aggregate(Sum('curr_load_mw'))
  demand = demand_query['curr_load_mw__sum']
  if demand == None:
    demand = 0
  if demand > supply:
    shortage = demand - supply
    grid_obj = Grid.objects
    grid_obj = grid_obj.first()
        
    if grid_obj:
      SheddingTarget.objects.create(zone=grid_obj, needed_red_mw=shortage, start_time=timezone.now(),
        expec_dura_mins=60, is_addressed=False)

      subject = 'grid shortage is detected'
      line1 = 'the system has detec. a power shortage.'
      line2 = 'demand: ' + str(demand) + ' MW'
      line3 = 'supply: ' + str(supply) + ' MW'
      line4 = 'shortage: ' + str(shortage) + ' MW'
            
      alert_message = line1 + " " + line2 + " " + line3 + " " + line4
            
      send_mail(subject, alert_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER],
        fail_silently=False)
            
      return 'the short. is detec. & the admin is notif.'
  return 'the grid bal is stable'
