from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect

from .forms import RegisterForm

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:list')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Добро пожаловать в Hop & Barley!'
            )

            return redirect('products:list')

    return render(
        request,
        'register.html',
        {'form': form}
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:list')

    if request.method == 'POST':
        email = request.POST.get('email','').strip().lower()
        password = request.POST.get('password','')
        user = authenticate(request, username=email, password=password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user)

            messages.success(
                request,
                'Вы успешно вошли в аккаунт!'
            )

            return redirect('products:list')

        messages.error(
            request,
            'Неверный email или пароль.'
        )

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('products:list')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('users:login')

    profile = request.user.profile

    return render(
        request,
        'profile.html',
        {'profile': profile}
    )


