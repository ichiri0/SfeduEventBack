from django.contrib import admin

from app.models import Departament, Direction, Group, Institute, GroupCourse, Role, UserProfile, Event, EventCategory
# Register your models here.


admin.site.register(Departament)
admin.site.register(Direction)
admin.site.register(Group)
admin.site.register(Institute)
admin.site.register(GroupCourse)
admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(EventCategory)