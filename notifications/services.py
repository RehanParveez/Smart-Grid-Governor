from economics.models import BillingAcc
from notifications.models import Alert
from notifications.tasks import alert_delivery

class PublicTransparency:
  @staticmethod
  def grid_warning(zone, payload):
    if zone is None:
      print('no zone is provided')
      return 
    print(f'zone {zone.name}')
    zone_recov = payload.get('recovery')
    if not zone_recov:
      zone_recov = 0
    accounts = BillingAcc.objects.filter(branch__transformer__feeder__substation__zone=zone).select_related('branch__transformer__feeder__finan_health', 'user')
    print(f'total accounts {accounts.count()}')

    for acc in accounts:
      print(f'alert {acc.user.username}')
      curr_feeder = acc.branch.transformer.feeder 
      local_reco = 0
      if hasattr(curr_feeder, 'finan_health'):
        health_rec = curr_feeder.finan_health
        local_reco = health_rec.reco_percent

      message = f'{zone.name} recovery is {zone_recov}%'
            
      if local_reco < 40:
        message += ' pay the bills to avoid load shedding'
      alert = Alert.objects.create(user=acc.user, account=acc, kind = 'warning', message=message[:70])
      alert_delivery.delay(alert.id)