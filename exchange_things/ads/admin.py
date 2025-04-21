from django.contrib import admin
from .models import Ad, ExchangeProposal


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'description', 'category',
                     'condition', 'created_at']


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ['id', 'ad_sender', 'ad_receiver', 'sender', 'receiver', 'comment', 'status']

