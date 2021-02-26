from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import User
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from schoolnn.views.mixins import UserIsWorkspaceAdminMixin
from django import forms


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "password"]


class UserListView(UserIsWorkspaceAdminMixin, ListView):
    model = User
    context_object_name = "users"
    template_name = "users/list.html"


class UserDetailView(UserIsWorkspaceAdminMixin, DetailView):
    model = User
    template_name = "users/detail.html"


class UserDeleteView(UserIsWorkspaceAdminMixin, DeleteView):
    model = User
    success_url = reverse_lazy("user-list")
    template_name = "users/delete.html"


class UserEditView(UserIsWorkspaceAdminMixin, UpdateView):
    model = User
    fields = ["username", "password"]
    template_name = "users/add.html"


class UserCreateView(UserIsWorkspaceAdminMixin, CreateView):
    form_class = UserForm
    template_name = "users/add.html"

    def form_valid(self, form):
        form.instance.password = make_password(form.instance.password)
        form.instance.workspace = self.request.user.workspace
        return super().form_valid(form)
