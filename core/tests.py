from django.test import TestCase
from .models import Socio
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class ModelTest(TestCase):
    def setUp(self):
        pass

    def test_notificar_email(self):
        socio = Socio.objects.create(
            user=User.objects.create_user(
                username='12345678',
                password='123456',
            ),
            nome='Fulano',
            stripe_customer_id='cus_123456789',
        )

        notificar = socio.notificar(metodo='email', mensagem='teste')

        self.assertEqual(notificar, 'Enviando email...')

    def test_datetime(self):
        current_period_end = datetime(
            2022, 6, 30, 23, 59, 59
        )
        if current_period_end - datetime.now() > timedelta(days=30):
            if datetime.now().month < 7:
                if current_period_end.month > 6:
                    current_period_end = datetime(
                        datetime.now().year, 6, 30, 23, 59, 59
                    )
