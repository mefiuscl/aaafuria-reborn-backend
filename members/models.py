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


class Attachment(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255, editable=False)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='members/attachments/', blank=True, null=True)

    def __str__(self) -> str:
        return self.title
