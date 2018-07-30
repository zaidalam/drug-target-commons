from django.contrib import admin
# from django.contrib.admin import AdminSite
from django.http import HttpResponse
# Register your models here.
from .models import SuggestionForReview



# class MyAdminSite(AdminSite):

#      def get_urls(self):
#          from django.conf.urls import url
#          urls = super(MyAdminSite, self).get_urls()
#          urls += [
#              url(r'^signup/$', self.admin_view(self.signup))
#          ]
#          return urls

#      def signup(self, request):
#          return HttpResponse("Hello!")




class SuggestionForReviewModelAdmin(admin.ModelAdmin):
	list_display=["__str__","time_stamp"]
	class Meta:
		model = SuggestionForReview


# admin_site = MyAdminSite()
admin.site.register(SuggestionForReview,SuggestionForReviewModelAdmin)