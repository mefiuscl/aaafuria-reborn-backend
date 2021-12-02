from django.db import models
from django.utils import timezone


class Conta(models.Model):
    socio = models.OneToOneField(
        'core.Socio', on_delete=models.CASCADE, related_name='conta')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    calangos = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.socio.nome

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'


# Model for transfering money between accounts
class Movimentacao(models.Model):
    conta_origem = models.ForeignKey(
        Conta, on_delete=models.CASCADE, related_name='transferencias_origem', blank=True, null=True)
    conta_destino = models.ForeignKey(
        Conta, on_delete=models.SET_NULL, related_name='transferencias_destino', blank=True, null=True)
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolvida = models.BooleanField(default=False)
    resolvida_em = models.DateTimeField(null=True, blank=True)
    estornada = models.BooleanField(default=False)
    estornada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'

    def __str__(self):
        return self.descricao

    def resolver(self):
        self.conta_origem.saldo -= self.valor
        self.conta_destino.saldo += self.valor

        self.resolvida = True
        self.resolvida_em = timezone.now()

        self.conta_destino.save()
        self.conta_origem.save()
        self.save()

    def estornar(self):
        self.conta_origem.saldo += self.valor
        self.conta_destino.saldo -= self.valor

        self.estornada = True
        self.estornada_em = timezone.now()

        self.conta_destino.save()
        self.conta_origem.save()
        self.save()

    def save(self, *args, **kwargs):
        super(Movimentacao, self).save(*args, **kwargs)

        if self.resolvida:
            if self.resolvida_em is None:
                self.resolver()
