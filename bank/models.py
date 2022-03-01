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
        return f'{self.socio}'

    class Meta:
        verbose_name = 'conta'
        verbose_name_plural = 'contas'


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
        verbose_name = 'movimentação'
        verbose_name_plural = 'movimentações'

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


class Resgate(models.Model):
    conta = models.ForeignKey(
        Conta, on_delete=models.CASCADE, related_name='resgates')
    descricao = models.CharField(max_length=100)
    valor_calangos = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolvida = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'resgate'
        verbose_name_plural = 'resgates'

    def __str__(self):
        return f'{self.conta}'

    def resolver(self):
        if not self.resolvida:
            if self.conta.calangos < self.valor_calangos:
                self.delete()
                raise Exception('Saldo insuficiente')

            self.conta.calangos -= self.valor_calangos
            self.resolvida = True
            self.conta.save()
            self.save()
        else:
            raise Exception('Resgate já resolvido')
