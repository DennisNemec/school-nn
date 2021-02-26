from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from schoolnn.models import User
from schoolnn.models import Workspace
from django.contrib.auth.models import Group


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)


class UserAdmin(BaseUserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "workspace"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Workspace)
admin.site.unregister(Group)
