
from activities.models import Activity, Category, Schedule
from django.test import TestCase
from django.utils import timezone


class ModelsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Esporte')
        self.activity = Activity.objects.create(
            name='Futsal',
            category=Category.objects.get(name='Esporte'),
        )

    def test_category_model(self):
        """
        Test the Category model
        """
        self.assertEqual(self.category.name, 'Esporte')

    def test_activity_model(self):
        """
        Test the Activity model
        """
        self.assertEqual(self.activity.name, 'Futsal')
        self.assertEqual(self.activity.category.name, 'Esporte')

    def test_schedule_model(self):
        """
        Test the Schedule model
        """
        schedule = Schedule.objects.create(
            description='Treino',
            status=Schedule.SCHEDULED,
            activity=Activity.objects.get(name='Futsal'),
            start_date=timezone.datetime(
                2022, 1, 1, 12, 0, 0, tzinfo=timezone.get_current_timezone()),
            location='UNINOVAFAPI',
            cost=100.50,
            max_participants=10,
            min_participants=1,
        )

        self.assertEqual(schedule.description, 'Treino')
        self.assertEqual(schedule.status, 'S')
        self.assertEqual(schedule.get_status_display(), 'Scheduled')
        self.assertEqual(schedule.activity.name, 'Futsal')
        self.assertEqual(schedule.start_date,
                         timezone.datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.get_current_timezone()))
        self.assertNotEqual(schedule.start_date,
                            timezone.datetime(2022, 1, 1, 13, 0, 0, tzinfo=timezone.get_current_timezone()))
        self.assertEqual(schedule.end_date, None)
        self.assertEqual(schedule.location, 'UNINOVAFAPI')
        self.assertEqual(schedule.get_cost(), 100.50)
        self.assertEqual(schedule.max_participants, 10)
        self.assertEqual(schedule.min_participants, 1)
        self.assertEqual(schedule.is_active, True)
        self.assertEqual(schedule.users_confirmed.all().count(), 0)
        self.assertEqual(schedule.users_present.all().count(), 0)

        # Teste remove cost with attachment deleting
        schedule.cost = None
        schedule.save()
        self.assertEqual(schedule.get_cost(), None)
