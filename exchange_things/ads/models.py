from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    CHOICES = (
        ('б/у', 'б/у'),
        ('новый', 'новый'),
    )
    user = models.ForeignKey(User,
                            related_name='ads',
                            on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='ads/%Y/%m/%d',
                            blank=True)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=50, choices=CHOICES, default='б/у')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    CHOICES = (
        ('Отклонена', 'Отклонена'),
        ('Ожидает', 'Ожидает'),
        ('Принята', 'Принята'),
    )
    ad_sender = models.ForeignKey(Ad,
                                related_name='ad_sended',
                                on_delete=models.CASCADE)
    sender = models.ForeignKey(User,
                                related_name='sended',
                                on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad,
                                related_name='ad_receiver',
                                on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,
                                related_name='received',
                                on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=9, choices=CHOICES, default='Ожидает')
    created_at = models.DateTimeField(auto_now_add=True)


