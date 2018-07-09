from django.contrib import admin
from battlesheep.models import Game, Ship, Shot


class ShipInline(admin.TabularInline):
    model = Ship


class ShotInline(admin.TabularInline):
    model = Shot


class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'started', 'ended')
    exclude = ('board',)
    inlines = [
        ShipInline,
        ShotInline
    ]


admin.site.register(Game, GameAdmin)
admin.site.register(Shot)
