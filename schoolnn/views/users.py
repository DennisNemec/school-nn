from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import User
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from schoolnn.views.mixins import UserIsWorkspaceAdminMixin
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "password"]


class UserListView(UserIsWorkspaceAdminMixin, ListView):
    model = User
    context_object_name = "detail_users"
    template_name = "users/list.html"


class UserDetailView(UserIsWorkspaceAdminMixin, DetailView):
    model = User
    context_object_name = "detail_user"
    template_name = "users/detail.html"


class UserDeleteView(UserIsWorkspaceAdminMixin, DeleteView):
    model = User
    context_object_name = "detail_user"
    success_url = reverse_lazy("user-list")
    template_name = "users/delete.html"

    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        messages.success(
            self.request, f"Benutzer „{user.username}“ erfolgreich gelöscht."
        )

        user.delete()

        return HttpResponseRedirect(self.success_url)


class UserEditView(UserIsWorkspaceAdminMixin, UpdateView):
    model = User
    context_object_name = "detail_user"
    form_class = UserForm
    template_name = "users/edit.html"

    def form_valid(self, form):
        user = self.get_object()

        form.instance.password = make_password(form.instance.password)

        messages.success(
            self.request, f"Nutzer „{user.username}“ erfolgreich editiert."
        )
        return super().form_valid(form)


class UserCreateView(UserIsWorkspaceAdminMixin, CreateView):
    form_class = UserForm
    template_name = "users/add.html"

    def form_valid(self, form: UserForm):
        form.instance.password = make_password(form.instance.password)
        form.instance.workspace = self.request.user.workspace

        messages.success(
            self.request,
            "Benutzer „{}“ erfolgreich erstellt.".format(
                form.cleaned_data["username"]
            ),
        )

        return super().form_valid(form)
