from celery import shared_task
from resources.models import GenerationUnit
from django.db.models import Sum
from decimal import Decimal
from topology.models import Feeder
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def min_grid_load():
  supply_query = GenerationUnit.objects.filter(operational=True).aggregate(total=Sum('curr_output_mw'))
  tot_supply = supply_query['total']
    
  if tot_supply is None:
    tot_supply = Decimal('0.00')
  demand_query = Feeder.objects.aggregate(total=Sum('curr_load_mw'))
  tot_demand = demand_query['total']
    
  if tot_demand is None:
    tot_demand = Decimal('0.00')
  grid_gap = tot_supply - tot_demand

  print(f'natio grid rep')
  print(f'tot supply: {tot_supply} MW')
  print(f'tot demand: {tot_demand} MW')
  print(f'curr gap: {grid_gap} MW')

  if grid_gap < 0:
    subject = f'grid fefic ({grid_gap} MW)'
    email_body = f"""
    the power deficit.
        
    curr supply: {tot_supply} MW
    curr demand: {tot_demand} MW
    gap: {grid_gap} MW
    now initia the load shedding.
    """
    
    send_mail(subject, email_body, settings.EMAIL_HOST_USER, ['rehanrural@gmail.com'], fail_silently=False)
    print('alert email is sent')

  return grid_gap