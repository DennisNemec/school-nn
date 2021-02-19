from django.contrib.auth.views import LoginView


class AuthLoginView(LoginView):
    template_name = "auth/login.html"
