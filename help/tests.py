from core.models import Socio
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django.test import TestCase

from .models import Issue


class IssueModelTest(TestCase):
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

    def test_issue_model(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            priority=Issue.PRIORITY_LOW,
            category=Issue.CATEGORY_OUTRA,
        )

        self.assertEqual(Issue.objects.count(), 1)

        issue = Issue.objects.first()
        self.assertEqual(issue.title, 'Teste')
        self.assertEqual(issue.description, 'Teste')
        self.assertEqual(issue.status, Issue.STATUS_OPEN)
        self.assertEqual(issue.priority, Issue.PRIORITY_LOW)
        self.assertEqual(issue.category, Issue.CATEGORY_OUTRA)

    def test_open_issue(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            category=Issue.CATEGORY_OUTRA,
        )

        issue = Issue.objects.first()
        self.assertEqual(issue.status, Issue.STATUS_OPEN)

    def test_in_progress_issue(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            category=Issue.CATEGORY_OUTRA,
        )

        issue = Issue.objects.first()
        issue.status = Issue.STATUS_IN_PROGRESS
        issue.save()

        self.assertEqual(issue.status, Issue.STATUS_IN_PROGRESS)

    def test_close_issue(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            category=Issue.CATEGORY_OUTRA,
        )

        issue = Issue.objects.first()
        issue.status = Issue.STATUS_CLOSED
        issue.save()

        self.assertEqual(issue.status, Issue.STATUS_CLOSED)

    def test_priority(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            category=Issue.CATEGORY_OUTRA,
        )

        issue = Issue.objects.first()
        issue.priority = Issue.PRIORITY_HIGH
        issue.save()

        self.assertEqual(issue.priority, Issue.PRIORITY_HIGH)


class CommentModelTest(TestCase):
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

    def test_comment_model(self):
        Issue.objects.create(
            author=Socio.objects.first(),
            title='Teste',
            description='Teste',
            category=Issue.CATEGORY_OUTRA,
        )

        issue = Issue.objects.first()
        issue.comments.create(
            description='Teste',
            author=Socio.objects.get(user__username='00000000'),
        )
        issue.check_status()
        issue.save()

        self.assertEqual(issue.comments.count(), 1)
        self.assertEqual(issue.status, Issue.STATUS_IN_PROGRESS)

        comment = issue.comments.first()
        self.assertEqual(comment.description, 'Teste')
        self.assertEqual(comment.get_author_apelido(), 'João')
