from django.db import models
from django.utils import timezone
from babel.dates import format_datetime, get_timezone

CATEGORIA_ATIVIDADE = (
    ('Diretoria', 'Diretoria'),
    ('Coord', 'Coordenação'),
    ('Esporte', 'Esporte'),
    ('Bateria', 'Bateria'),
    ('Social', 'Ação social'),
    ('Outra', 'Outra'),
)

PROGRAMACAO_ESTADOS = (
    ('Agendado', 'Agendado'),
    ('Confirmado', 'Confirmado'),
    ('Cheio', 'Cheio'),
    ('Aguardando', 'Aguardando competidores'),
)


class Competidor(models.Model):
    socio = models.OneToOneField(
        'core.Socio', on_delete=models.CASCADE, related_name='competidor')

    def __str__(self):
        return f'{self.socio}'

    class Meta:
        verbose_name = 'competidor'
        verbose_name_plural = 'competidores'


class Modalidade(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_ATIVIDADE)
    competidores = models.ManyToManyField(
        'Competidor', blank=True, related_name='modalidades')
    responsavel = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, related_name='modalidades', blank=True, null=True, editable=False)

    def __str__(self):
        return self.nome

    # Define o usuário da requisição como responsavel
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Programacao(models.Model):
    modalidade = models.ForeignKey(
        'Modalidade', on_delete=models.CASCADE, related_name='programacao')
    data_hora = models.DateTimeField(default=timezone.now)
    local = models.CharField(max_length=100)
    descricao = models.TextField()

    competidores_confirmados = models.ManyToManyField(
        'Competidor', blank=True, related_name='confirmados_na_programacao')
    competidores_presentes = models.ManyToManyField(
        'Competidor', blank=True, related_name='presentes_na_programacao')

    competidores_minimo = models.IntegerField(default=0)  # default no min
    competidores_maximo = models.IntegerField(default=0)  # default no max

    grupo_whatsapp_url = models.CharField(
        max_length=150, blank=True, null=True)

    estado = models.CharField(max_length=20, default='Agendado')

    class Meta:
        verbose_name = 'programação'
        verbose_name_plural = 'programações'

    def __str__(self):
        datetime = format_datetime(self.data_hora, locale="pt_BR",
                                   format="dd/MM/yyyy HH:mm", tzinfo=get_timezone('America/Sao_Paulo'))
        return f'{self.modalidade} - {datetime}'

    @property
    def finalizado(self):
        if self.data_hora < timezone.now():
            self.estado = 'Finalizado'
            self.save()
            return True
        return False

    def checar_estado(self):
        if self.competidores_confirmados.count() >= self.competidores_minimo:
            if self.competidores_confirmados.count() == 0:
                self.estado = 'Agendado'
            else:
                self.estado = 'Confirmado'

            if self.competidores_maximo != 0 and self.competidores_confirmados.count() == self.competidores_maximo:
                self.estado = 'Cheio'
        else:
            self.estado = 'Aguardando'

        self.save()
        return self.estado

    def notificar_confirmacao(self):
        self.save()

        subject = 'Programação confirmada'
        message = 'Confirmados: \n'
        for competidor in self.competidores_confirmados.all():
            message += f'{competidor.socio}' + '\n'

        context = {
            message: message,
        }

        self.modalidade.responsavel.notificar('email', subject,
                                              'programacao_confirmada.txt', 'programacao_confirmada.html', context)
