from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class Activity(models.Model):
    name = models.CharField(max_length=100)
    first_team = models.ManyToManyField(
        'auth.User', blank=True)
    category = models.ForeignKey(
        'activities.Category', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class Schedule(models.Model):
    WAITING = 'W'
    CONFIRMED = 'C'
    ENDED = 'E'
    STATUS_CHOICES = (
        (WAITING, _('Waiting')),
        (CONFIRMED, _('Confirmed')),
        (ENDED, _('Ended')),
    )

    activity = models.ForeignKey(
        'Activity', on_delete=models.CASCADE, related_name='schedules')
    description = models.TextField()
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=WAITING)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=100)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    max_participants = models.IntegerField()
    min_participants = models.IntegerField()
    is_active = models.BooleanField(default=True)
    users_confirmed = models.ManyToManyField(
        'auth.User', blank=True, related_name='confirmed_schedules')
    users_present = models.ManyToManyField(
        'auth.User', blank=True, related_name='present_schedules')

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        ordering = ['start_date']

    def __str__(self):
        return self.activity.name + ' - ' + timezone.localtime(self.start_date).strftime('%d/%m/%Y %H:%M')

    def get_cost(self):
        attach = self.attachments.filter(title='cost').first()
        if attach:
            return float(attach.content)
        return None

    def refresh(self):
        if self.users_confirmed.count() >= self.min_participants:
            self.status = self.CONFIRMED
        else:
            self.status = self.WAITING

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.cost:
            attach, created = self.attachments.get_or_create(
                title='cost')
            attach.content = self.cost
            attach.save()
        else:
            self.attachments.filter(title='cost').delete()


class Attachment(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='activity/attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')
        ordering = ['title']

    def __str__(self) -> str:
        return self.title
