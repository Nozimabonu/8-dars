from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from blog import forms
from blog.forms import RegisterForm, EmailForm
from blog.models import User
from blog.views.tokens import account_activation_token


# def login_page(request):
#     form = LoginForm()
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, email=email, password=password)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('index')
#             else:
#                 messages.add_message(
#                     request,
#                     level=messages.WARNING,
#                     message='User not found'
#
#                 )
#
#     return render(request, 'blog/auth/login.html', {'form': form})

# View
# class LoginPageView(View):
#     def get(self, request):
#         form = LoginForm()
#         return render(request, 'blog/auth/login.html', {'form': form})
#
#     def post(self, request):
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, email=email, password=password)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('index')
#             else:
#                 messages.add_message(
#                     request,
#                     level=messages.WARNING,
#                     message='User not found'
#                 )
#         return render(request, 'blog/auth/login.html', {'form': form})

class MyLoginView(LoginView):
    template_name = 'blog/auth/login.html'
    success_url = reverse_lazy('blog:my_success_view')

def logout_page(request):
    logout(request)
    return redirect(reverse('index'))


# def register(request):
#     form = RegisterForm()
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data.get('first_name')
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             user = User.objects.create_user(first_name=first_name, email=email, password=password)
#             user.is_active = False
#             user.is_staff = True
#             user.is_superuser = True
#             user.save()
#             current_site = get_current_site(request)
#             subject = 'Verify your email'
#             message = render_to_string('blog/auth/email/activation.html',
#                                        {
#                                            'request': request,
#                                            'user': user,
#                                            'domain': current_site.domain,
#                                            'uid': urlsafe_base64_encode(force_bytes(user.id)),
#                                            'token': account_activation_token.make_token(user)
#                                        })
#             email = EmailMessage(subject, message, to=[email])
#             email.content_subtype = 'html'
#             email.send()
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#             return redirect('verify_email_done')
#
#             # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#             # return redirect('index')
#
#     return render(request, 'blog/auth/register.html', {'form': form})

# View
class RegisterView(View):
    form_class = RegisterForm
    template_name = 'blog/auth/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(first_name=first_name, email=email, password=password)
            user.is_active = False
            user.is_staff = True
            user.is_superuser = True
            user.save()
            current_site = get_current_site(request)
            subject = 'Verify your email'
            message = render_to_string('blog/auth/email/activation.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user)
            })
            email_message = EmailMessage(subject, message, to=[email])
            email_message.content_subtype = 'html'
            email_message.send()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('verify_email_done')

        return render(request, self.template_name, {'form': form})


# views.py

# def sending_email(request):
#     sent = False
#
#     if request.method == 'POST':
#         form = EmailForm(request.POST)
#         subject = request.POST.get('subject')
#         message = request.POST.get('message')
#         from_email = request.POST.get('from_email')
#         to = request.POST.get('to')
#         send_mail(subject, message, from_email, [to])
#         sent = True
#     else:
#         form = EmailForm()
#
#     return render(request, 'blog/sending-email.html', {'form': form, 'sent': sent})
class SendingEmailView(View):
    template_name = 'blog/sending-email.html'

    def get(self, request):
        form = EmailForm()
        return render(request, self.template_name, {'form': form, 'sent': False})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')
            from_email = form.cleaned_data.get('from_email')
            to = form.cleaned_data.get('to')
            send_mail(subject, message, from_email, [to])
            return render(request, self.template_name, {'form': form, 'sent': True})

        return render(request, self.template_name, {'form': form, 'sent': False})

# def verify_email_done(request):
#     return render(request, 'blog/auth/email/verify-email-done.html')


class VerifyEmailDoneView(View):
    template_name = 'blog/auth/email/verify-email-done.html'
    def get(self, request):
        return render(request, self.template_name)


# def verify_email_confirm(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         return redirect('verify_email_complete')
#     else:
#         messages.warning(request, 'The link is invalid.')
#     return render(request, 'blog/auth/email/verify-email-confirm.html')

class VerifyEmailConfirmView(View):
    template_name = 'blog/auth/email/verify-email-confirm.html'
    success_url = reverse_lazy('verify_email_complete')

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect(self.success_url)
        else:
            messages.warning(request, 'The link is invalid.')

        return render(request, self.template_name)

# def verify_email_complete(request):
#     return render(request, 'blog/auth/email/verify-email-complete.html')

class VerifyEmailCompleteView(View):
    template_name = 'blog/auth/email/verify-email-complete.html'

    def get(self, request):
        return render(request, self.template_name)
