from django.test import TestCase
from .models import Socio
from django.contrib.auth.models import User


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
