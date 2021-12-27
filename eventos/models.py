from django.db import models


class Participante(models.Model):
    socio = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, blank=True, null=True)

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    whatsapp = models.CharField(max_length=25)
    rg = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()

    categoria = models.CharField(
        max_length=12,
        choices=(
            ('socio', 'Sócio'),
            ('n_socio', 'Não sócio'),
            ('convidado', 'Convidado'),
            ('organizador', 'Organizador'),
        ),
        default='n_socio',
    )

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.socio:
            self.nome = self.socio.nome
            self.email = self.socio.user.email
            self.whatsapp = self.socio.whatsapp
            self.rg = self.socio.rg
            self.cpf = self.socio.cpf
            self.data_nascimento = self.socio.data_nascimento

            if self.socio.is_socio:
                self.categoria = 'socio'
        else:
            self.categoria = 'convidado'

        super().save(*args, **kwargs)


class Convidado(models.Model):
    participante_responsavel = models.ForeignKey(
        Participante, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.nome


class Evento(models.Model):
    nome = models.CharField(max_length=100)
    participantes = models.ManyToManyField(Participante)

    def __str__(self):
        return self.nome


class Lote(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    preco_socio = models.DecimalField(max_digits=7, decimal_places=2)
    preco_convidado = models.DecimalField(max_digits=7, decimal_places=2)
    quantidade_restante = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return self.nome


class Ingresso(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    data_compra = models.DateField(auto_now_add=True)
    valor = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(
        max_length=12,
        choices=(
            ('pago', 'Pago'),
            ('pendente', 'Pendente'),
            ('cancelado', 'Cancelado'),
        )
    )

    def __str__(self):
        return self.participante.nome

    def set_valor(self):
        categoria = {
            'socio': self.lote.preco_socio,
            'n_socio': self.lote.preco,
            'convidado': self.lote.preco_convidado,
        }

        self.valor = categoria[self.participante.categoria]

    def save(self, *args, **kwargs):
        self.set_valor()
        super().save(*args, **kwargs)
