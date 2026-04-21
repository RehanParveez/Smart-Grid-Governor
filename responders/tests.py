from accounts.tests import ParentTest
from responders.models import Team
from topology.models import Substation, Feeder
from django.contrib.contenttypes.models import ContentType
from tasks.models import Maintenance
from django.urls import reverse
from topology.models import Grid

class RespondersSignalTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.team = Team.objects.create(name = 'A squad', zone=self.zone_a, leader=self.officer_b, is_active=True)
    self.sub = Substation.objects.create(zone=self.zone_a, name = 'Sub Res', max_capa_mw=50.0)
    self.feeder = Feeder.objects.create(substation=self.sub, code = 'F-TASK', curr_load_mw=5.0)
    self.feeder_type = ContentType.objects.get_for_model(self.feeder)

    self.task = Maintenance.objects.create(subject = 'transformer repair', content_type=self.feeder_type, object_id=self.feeder.id,
      assigned=self.team, status = 'ongoing')

  def test_team_deact_resets_tasks(self):
    self.team.is_active = False
    self.team.save()
    self.task.refresh_from_db()
    self.assertEqual(self.task.status, 'assigned')
    self.assertIsNone(self.task.assigned)

  def test_active_team_save_doesnt_reset_tasks(self):
    self.team.name = 'A squad updated'
    self.team.save()
    self.task.refresh_from_db()
    self.assertEqual(self.task.status, 'ongoing')
    self.assertEqual(self.task.assigned, self.team)

  def test_solved_tasks_not_affec_by_deact(self):
    self.task.status = 'solved'
    self.task.save()
    self.team.is_active = False
    self.team.save()
    self.task.refresh_from_db()
    self.assertEqual(self.task.status, 'solved')
    self.assertIsNotNone(self.task.assigned)

class TeamViewSetTest(ParentTest):
  def setUp(self):
    super().setUp()
    self.list_url = reverse('team-list')

  def test_get_queryset_filtering(self):
    Team.objects.create(name = 'Zone A Team', zone=self.zone_a)
    other_zone = Grid.objects.create(name = 'Zone 99')
    Team.objects.create(name = 'Foreign Team', zone=other_zone)
    self.auth(self.engineer_a)
    resp = self.client.get(self.list_url)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(len(resp.data), 1)
    self.assertEqual(resp.data[0]['name'], 'Zone A Team')

  def test_perform_create_zone_enforcement(self):
    self.auth(self.engineer_a)
    data = {'name': 'Tech Squad', 'leader': self.officer_b.id} 
    resp = self.client.post(self.list_url, data)
    print(f'\nDEBUG ERROR DATA: {resp.data}')
    self.assertEqual(resp.status_code, 201)
    team = Team.objects.get(name = 'Tech Squad')
    self.assertEqual(team.zone, self.zone_a) 

  def test_admin_can_create_in_any_zone(self):
    zone_c = Grid.objects.create(name = 'Zone C')
    self.auth(self.admin)
    data = {'name': 'Team Admin', 'zone': zone_c.id, 'leader': self.officer_b.id}
    resp = self.client.post(self.list_url, data)
    self.assertEqual(resp.status_code, 201)
    team = Team.objects.get(name = 'Team Admin')
    self.assertEqual(team.zone, zone_c) 