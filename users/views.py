from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from orders.models import Order

from .forms import (
    ProfileForm,
    RegisterForm,
    UserPasswordChangeForm,
)
from .models import Profile

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:list')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()

            Profile.objects.get_or_create(
                user=user,
            )

            login(request, user)

            messages.success(
                request,
                'Добро пожаловать в Hop & Barley!',
            )

            return redirect('products:list')

    return render(
        request,
        'register.html',
        {
            'form': form,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:list')

    if request.method == 'POST':
        email = request.POST.get(
            'email',
            '',
        ).strip().lower()

        password = request.POST.get(
            'password',
            '',
        )

        try:
            user = User.objects.get(
                email__iexact=email,
            )
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user)

            Profile.objects.get_or_create(
                user=user,
            )

            messages.success(
                request,
                'Вы успешно вошли в аккаунт!',
            )

            return redirect('products:list')

        messages.error(
            request,
            'Неверный email или пароль.',
        )

    return render(
        request,
        'login.html',
    )


def logout_view(request):
    logout(request)

    messages.info(
        request,
        'Вы вышли из аккаунта.',
    )

    return redirect('products:list')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('users:login')

    profile, created = Profile.objects.get_or_create(
        user=request.user,
    )

    return render(
        request,
        'profile.html',
        {
            'profile': profile,
        },
    )


@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
    )

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Профиль успешно обновлён.',
            )

            return redirect('users:profile')

    else:
        form = ProfileForm(
            instance=profile,
        )

    return render(
        request,
        'profile_edit.html',
        {
            'form': form,
            'profile': profile,
        },
    )


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(
            request.user,
            request.POST,
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                'Пароль успешно изменён.',
            )

            return redirect('users:profile')

    else:
        form = UserPasswordChangeForm(
            request.user,
        )

    return render(
        request,
        'password_change.html',
        {
            'form': form,
        },
    )


@login_required
def order_history_view(request):
    orders = (
        Order.objects
        .filter(
            user=request.user,
        )
        .prefetch_related(
            'items__product',
        )
    )

    status = request.GET.get(
        'status',
        '',
    ).strip()

    valid_statuses = {
        value
        for value, label in Order.Status.choices
    }

    if status in valid_statuses:
        orders = orders.filter(
            status=status,
        )
    else:
        status = ''

    return render(
        request,
        'order_history.html',
        {
            'orders': orders,
            'selected_status': status,
            'status_choices': Order.Status.choices,
        },
    )

