from django.db import models


def member_avatar_dir(instance, filename):
    return 'members/avatars/{0}/{1}'.format(instance.user.username, filename)


class Member(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    registration = models.CharField(max_length=8, default='00000000')
    group = models.CharField(max_length=7, default='MED: 00')

    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=124)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=15)
    birth_date = models.DateField()

    avatar = models.ImageField(
        upload_to=member_avatar_dir, blank=True, null=True)
    rg = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def has_active_membership(self):
        from memberships.models import Membership
        membership = Membership.objects.filter(is_active=True).first()
        if membership.exists() and membership.is_active:
            return True
        return False

    @property
    def active_membership(self):
        return self.get_active_membership()

    @property
    def first_teamer(self):
        from atividades.models import Modalidade
        for modalidade in Modalidade.objects.all():
            if not self.user.socio.competidor:
                return False
            if self.user.socio.competidor in modalidade.competidores.all():
                return True
        return False

    def get_active_membership(self):
        return self.memberships.filter(is_active=True).first() if self.has_active_membership else None

    def clean(self):
        self.name = self.name.upper()
        self.nickname = self.nickname.upper()
        self.email = self.email.lower()
        self.phone = self.phone.replace(
            '(', '').replace(')', '').replace('-', '')
        self.rg = self.rg.replace('.', '').replace(
            '-', '') if self.rg else None
        self.cpf = self.cpf.replace('.', '').replace(
            '-', '') if self.cpf else None

        return super().clean()


class Attachment(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255, editable=False)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='members/attachments/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
