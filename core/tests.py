from django.test import TestCase
from model_bakery import baker
import pprint

# Create your tests here.


class SocioTest(TestCase):
    def test_create_socio(self):
        print('Testando criação de sócio...')
        socio = baker.make("core.Socio", nome="Teste")
        self.assertTrue(socio)

    def test_create_socio_with_nome(self):
        print('Testando criação de sócio com nome...')
        socio = baker.make("core.Socio", nome="Teste Completo")
        self.assertEqual(str(socio), "TESTE COMPLETO")

    def test_create_socio_with_apelido(self):
        print('Testando criação de sócio com apelido...')
        socio = baker.make(
            "core.Socio", nome="Teste Completo", apelido="Teste")
        self.assertEqual(str(socio), "Teste")
        self.assertNotEqual(str(socio), "Teste Completo")
