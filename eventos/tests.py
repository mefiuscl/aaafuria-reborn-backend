import datetime

from core.models import Socio
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Convidado, Evento, Ingresso, Lote, Participante


class ParticipanteModelTest(TestCase):
    def setUp(self):
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

    def test_participante_str(self):
        print('test_participante_str')
        participante = Participante(nome='João')
        self.assertEqual(str(participante), 'João')

    def test_participante_str_socio(self):
        print('test_participante_str_socio')
        socio = Socio.objects.get(matricula='00000000')

        participante = Participante(
            socio=socio,
        )

        participante.save()

        self.assertEqual(str(participante), 'JOÃO DE SOUZA')

    def test_participante_categoria(self):
        print('test_participante_categoria')
        socio = Socio.objects.get(matricula='00000000')

        participante = Participante(
            socio=socio,
        )
        participante.save()

        self.assertEqual(participante.categoria, 'n_socio')

        socio.is_socio = True
        participante.save()
        self.assertEqual(participante.categoria, 'socio')

    def test_convites_restantes(self):
        print('test_convites_restantes')
        socio = Socio.objects.get(matricula='00000000')

        participante = Participante(
            socio=socio,
        )
        participante.save()

        self.assertEqual(participante.convites_disponiveis, 1)

        participante.convites_disponiveis = 2
        participante.save()

        self.assertEqual(participante.convites_disponiveis, 2)


class ConvidadoModelTest(TestCase):
    def setUp(self):
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

        Evento(nome='Evento Teste',
               data_inicio=timezone.make_aware(
                   datetime.datetime(2020, 1, 1, 15, 0)),
               data_fim=timezone.make_aware(
                   datetime.datetime(2020, 1, 1, 15, 0))
               ).save()

    def test_convidado_str(self):
        print('test_convidado_str')
        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'))
        participante.save()

        convidado = Convidado(
            participante_responsavel=participante,
            evento=Evento.objects.get(nome='Evento Teste'),
            nome='João de Souza',
        )

        convidado.save()

        self.assertEqual(str(convidado), 'João de Souza')

    def test_convidar(self):
        print('test_convidar')
        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'),
        )
        participante.save()

        if participante.convites_disponiveis > 0:
            convidado = Convidado(
                participante_responsavel=participante,
                evento=Evento.objects.get(nome='Evento Teste'),
                nome='João de Souza',
                email='convidado@email.com'
            )
            convidado.save()

            participante.convites_disponiveis -= 1
            participante.save()

            self.assertEqual(Convidado.objects.all(
            ).first().email, 'convidado@email.com')
            self.assertEqual(Convidado.objects.count(), 1)
            self.assertEqual(convidado.evento.nome, 'Evento Teste')

            self.assertEqual(participante.convites_disponiveis, 0)

        else:
            self.assertEqual(Convidado.objects.count(), 0)
            self.assertEqual(participante.convites_disponiveis, 0)

    def test_aprovar_convidado(self):
        print('test_aprovar_convidado')
        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'),
        )
        participante.save()

        convidado = Convidado(
            participante_responsavel=participante,
            nome='João de Souza',
            email='convidado@email.com'
        )

        convidado.aprovar()
        convidado.save()

        self.assertEqual(convidado.aprovado, True)


class EventoModelTest(TestCase):
    def test_evento_str(self):
        print('test_evento_str')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))

        self.assertEqual(str(evento), 'Evento Teste')

    def test_criar_evento(self):
        print('test_criar_evento')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        self.assertEqual(Evento.objects.count(), 1)


class LoteModelTest(TestCase):
    def test_criar_lote(self):
        print('test_criar_lote')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0), timezone.get_current_timezone()), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        self.assertEqual(Lote.objects.count(), 1)


class IngressoModelTest(TestCase):
    def setUp(self):
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

    def test_criar_ingresso(self):
        print('test_criar_ingresso')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'),)

        participante.save()

        Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        self.assertEqual(Ingresso.objects.count(), 1)

    def test_valor_ingresso_n_socio(self):
        print('test_valor_ingresso_n_socio')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'),)

        participante.save()

        ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        self.assertEqual(ingresso.valor, 100)

    def test_valor_ingresso_socio(self):
        print('test_valor_ingresso_socio')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        socio = Socio.objects.get(matricula='00000000')
        socio.is_socio = True
        socio.save()

        participante = Participante(
            socio=socio,)

        participante.save()

        ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        self.assertEqual(ingresso.valor, 70)

    def test_valor_ingresso_convidado(self):
        print('test_valor_ingresso_convidado')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            nome='João de Souza',
            email='joao@email.com',
            whatsapp='(86) 9 9123-4567',
            rg='123456789',
            cpf='123.456.789-00',
            data_nascimento='2000-01-01',
        )

        participante.save()

        ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        self.assertEqual(ingresso.valor, 130)

    def test_quantidade_restante(self):
        print('test_quantidade_restante')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            socio=Socio.objects.get(matricula='00000000'),)

        participante.save()

        ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        ingresso.lote.quantidade_restante -= 1

        self.assertEqual(ingresso.lote.quantidade_restante, 1)

    def test_stripe_checkout_session(self):
        print('test_stripe_checkout_session')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            nome='João de Souza',
            email='joao@email.com',
            whatsapp='(86) 9 9123-4567',
            rg='123456789',
            cpf='123.456.789-00',
            data_nascimento='2000-01-01',
        )

        participante.save()

        ingresso: Ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        ingresso.save()

        ingresso.create_stripe_checkout()
        ingresso.save()
        self.assertEqual(ingresso.status, 'aguardando')

    def test_ingresso_set_paid(self):
        print('test_ingresso_set_paid')
        evento = Evento(nome='Evento Teste',
                        data_inicio=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)), data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)))
        evento.save()

        lote = Lote(
            evento=evento,
            nome='Lote Teste',
            preco=100,
            preco_socio=70,
            preco_convidado=130,
            quantidade_restante=2,
            data_inicio=timezone.make_aware(
                datetime.datetime(2020, 1, 1, 15, 0)),
            data_fim=timezone.make_aware(datetime.datetime(2020, 1, 1, 15, 0)),
        )

        lote.save()

        participante = Participante(
            nome='João de Souza',
            email='joao@email.com',
            whatsapp='(86) 9 9123-4567',
            rg='123456789',
            cpf='123.456.789-00',
            data_nascimento='2000-01-01',
        )

        participante.save()

        ingresso: Ingresso = Lote.objects.get(nome='Lote Teste').ingresso_set.create(
            participante=participante,
            lote=lote,
        )

        ingresso.set_paid()

        self.assertEqual(ingresso.status, 'pago')
        self.assertEqual(ingresso.lote.quantidade_restante, 1)
        self.assertEqual(ingresso.lote.evento.participantes.count(), 1)
