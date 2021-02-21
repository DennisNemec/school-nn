from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView


class AuthMixin(LoginRequiredMixin):
    """ Require the user to be logged in. """

    login_url = "/login"


class AuthenticatedCreateView(LoginRequiredMixin, CreateView):
    """ Set the user attribute the the logged in user """

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
