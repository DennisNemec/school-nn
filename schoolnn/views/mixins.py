from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView


from schoolnn.models import Project, TrainingPass


class UserIsProjectOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Test if the user is the owner of the project specified as project_pk.
    """

    def test_func(self):
        project = Project.objects.filter(
            pk=self.kwargs["project_pk"], user=self.request.user
        ).first()

        if project is None:
            return False

        if "training_pk" not in self.kwargs.values():
            return True

        return TrainingPass.objects.filter(
            pk=self.kwargs["training_pk"], project=project
        ).exists()


class AuthenticatedQuerysetMixin(LoginRequiredMixin):
    """ Only show objects create by the user in the results. """

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class AuthenticatedCreateView(LoginRequiredMixin, CreateView):
    """ Set the user attribute the the logged in user """

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserIsWorkspaceAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
