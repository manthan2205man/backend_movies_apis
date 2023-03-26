from django.contrib import admin
from . models import *

class UserAdmin(admin.ModelAdmin):
    list_display  = ['username', 'id']
    list_filter = ['is_delete']


admin.site.register(User, UserAdmin)
admin.site.register(UserToken)
admin.site.register(Movie)
admin.site.register(Collection)
admin.site.register(RequestCount)