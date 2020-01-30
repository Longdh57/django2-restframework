from django.contrib import admin
from .models import ProportionKpiTeam, ExchangePointPos365


@admin.register(ProportionKpiTeam)
class ProportionKpiTeamAdmin(admin.ModelAdmin):
    list_display = ('area', 'type', 'leader_coefficient')


@admin.register(ExchangePointPos365)
class ExchangePointPos365Admin(admin.ModelAdmin):
    list_display = ('type', 'point')
