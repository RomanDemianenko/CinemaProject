from django.contrib import admin
from mysite.models import MyUser, Seance, Order, Hall

# Register your models here.
admin.site.register(Hall)
admin.site.register(MyUser)
admin.site.register(Seance)
admin.site.register(Order)