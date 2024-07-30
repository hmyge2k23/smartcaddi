from django.shortcuts import redirect, render 
from .forms import CreateUser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Connexion
def loginPage(request):
    error = None
    if request.method == 'POST':
        name_user = request.POST.get('username')
        pwd_user = request.POST.get('password')
        
        user = authenticate(username=name_user, password=pwd_user)
        if user is not None:
            # user.statut = True
            # user.save()
            login(request, user)
            return redirect('acceuil')
        else :
            error = 'Login/Mot de passe incorrect'
        if error:
            messages.error(request, error)
            return redirect('login')
    else:
        form = CreateUser()
    return render(request, "login.html", {'form': form}) 

# Déconnexion
def logoutPage(request):
    if request.user.is_authenticated:
        # request.user.statut = False
        # request.user.save()
        logout(request)
    return redirect('acceuil')
