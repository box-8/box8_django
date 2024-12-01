from django.http import request
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserRegistration, UserEditForm
from django.utils.translation import activate, deactivate, gettext_lazy as _


# Create your views here.

@login_required
def dashboard(request):
    context = {
        "welcome": "Bienvenue dans votre espace personnel"
    }
    return render(request, 'authapp/dashboard.html', context=context)


@login_required
def about(request):
    # initialisation des variables session 
    context = {
        "welcome": "A propos de Engineeria"
    }
    return render(request, 'authapp/about.html', context=context)


def register(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data.get('password'))
            new_user.save()
            return render(request, 'authapp/register_done.html')
    else:
        form = UserRegistration()

    form.fields['username'].label = _("Nom d'utilisateur")
    form.fields['email'].label = _('Adresse e-mail')
    form.fields['first_name'].label = _('Prénom')
    form.fields['last_name'].label = _('Nom de famille')
    form.fields['password'].label = _('Mot de passe')

    context = {"form": form}

    return render(request, 'authapp/register.html', context=context)


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    
    user_form.fields['email'].label = _('Nouvelle adresse e-mail')
    user_form.fields['first_name'].label = _('Nouveau prénom')
    user_form.fields['last_name'].label = _('Nouveau nom de famille')

    context = {
        'form': user_form,
    }
    return render(request, 'authapp/edit.html', context=context)
