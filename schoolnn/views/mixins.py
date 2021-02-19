from django.contrib.auth.mixins import LoginRequiredMixin


class AuthMixin(LoginRequiredMixin):
    """ Require the user to be logged in. """

    login_url = "/login"
