from builtins import super

from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import CreateView, FormView
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from .models import UserManager


# Create your views here.


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/accounts/login/'


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form, *args, **kwargs):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session['quest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                messages.info(self.request, 'put a valid email')
                return redirect(redirect_path)
            else:
                if request.user.is_admin or request.user.is_staff:
                    messages.info(self.request, 'welcome to the admin dashboard')
                    return redirect('products:admin-dashboard')
                else:
                    messages.info(self.request, 'welcome, we have all you need')
                    return redirect('products:product-list')
        return super(LoginView, self).form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
    # Redirect to a success page.
