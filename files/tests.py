from core.models import Socio
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from files.models import File


class FileModelTest(TestCase):
    def setUp(self) -> None:
        Socio(
            user=User.objects.create_user(
                username='00000000',
                password='000000'
            ),
            nome='João de Souza',
            apelido='João',
            whatsapp='(86) 9 9123-4567',
            cpf='123.456.789-00',
            rg='123456789',
            data_nascimento='2000-01-01',
            stripe_customer_id='cus_00000000',).save()

    def test_file_model(self):
        # Create a file
        file = File.objects.create(
            author=Socio.objects.get(user__username='00000000'),
            title='Test file',
            content='This is a test file',
            file=SimpleUploadedFile('test.txt', b'hello world'),
        )

        # Check that the file is saved
        self.assertTrue(file.pk > 0)

        # Check that the file is saved with the correct data
        self.assertEqual(file.title, 'Test file')

        # Check that the file is saved with the correct data
        self.assertEqual(file.content, 'This is a test file')

        # Check that the file is saved with the correct data
        self.assertEqual(file.file.name, 'files/test.txt')

        # Check that the file is saved with the correct data
        self.assertEqual(file.file.read(), b'hello world')

        # Check that the file is saved with the correct data
        self.assertEqual(file.author.user.username, '00000000')

        # Check that the file is saved with the correct data
        self.assertEqual(file.author.nome, 'JOÃO DE SOUZA')

    def test_view_file(self):
        # Create a file
        file: File = File.objects.create(
            author=Socio.objects.get(user__username='00000000'),
            title='Test file',
            content='This is a test file',
            file=SimpleUploadedFile('test.txt', b'hello world'),
        )

        file.viewers.add(Socio.objects.get(user__username='00000000'))

        file.save()
        # Check that the file is saved
        self.assertTrue(file.pk > 0)

        # Check the viewers count
        self.assertEqual(file.viewers.count(), 1)

    def test_like_file(self):
        # Create a file
        file: File = File.objects.create(
            author=Socio.objects.get(user__username='00000000'),
            title='Test file',
            content='This is a test file',
            file=SimpleUploadedFile('test.txt', b'hello world'),
        )

        file.likes.add(Socio.objects.get(user__username='00000000'))
        file.save()

        # Check that the file is saved
        self.assertTrue(file.pk > 0)

        # Check the likes count
        self.assertEqual(file.likes.count(), 1)
