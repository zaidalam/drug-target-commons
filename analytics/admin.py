from django.contrib import admin

# Register your models here.
from .models import Analytics

class AnalyticsModelAdmin(admin.ModelAdmin):
	class Meta:
		model = Analytics

admin.site.register(Analytics,AnalyticsModelAdmin)