import json
from django.utils import timezone
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from achats.models import Categorie, Fournisseur, Produit, SousCategorie, Profile
from achats.models import Paiement, Commande
from django.db.models import Q, Sum
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib.auth import update_session_auth_hash
import re
import csv
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import make_password


# Connexion / Déconnexion User
def loginPage(request):
    error = None
    if request.method == 'POST':
        name_user = request.POST.get('user_email')
        pwd_user = request.POST.get('password')
        
                # Vérifie si les champs sont vides et retourne la page sans erreur
        if not name_user or not pwd_user:
            return redirect('login')
        
        try:
            # Utiliser Q pour voir si c'est un email ou username afin de faire une requête complexe de manière simple
            user = User.objects.filter(Q(username=name_user) | Q(email=name_user)).first()
        except User.DoesNotExist:
            user = None
        
        
        if user is not None:
            # user.statut = True
            # user.save()
            user = authenticate(username=user.username, password=pwd_user)
            if user is not None:
                login(request, user)
                
                # Vérification du rôle de l'utilisateur
                if user.groups.filter(name='caissiere').exists():
                    return redirect('caiss_home')  
                elif user.groups.filter(name='tablette').exists():
                    return redirect('acceuil')  
                elif user.groups.filter(name='administrateur').exists():
                    return redirect('dash_home')  
            else:
                error = 'Login/Mot de passe incorrect'              
        else:   
            error = 'Login/Mot de passe incorrect'
        if error:
            messages.error(request, error)
            return redirect('login')
        
    return render(request, "cnx_user/index.html")

@login_required(login_url='login')
def logoutPage(request):
    if request.user.is_authenticated:
        # request.user.statut = False
        # request.user.save()
        
        # Récupérer le rôle du User pendant qu'il est connecté 
        if request.user.groups.filter(name='caissiere').exists() or request.user.groups.filter(name='administrateur').exists():
            redirect_url = 'login' 
        else:
            redirect_url = 'acceuil' 
            
        logout(request)
        return redirect(redirect_url)
    return redirect('acceuil')

def reset_pwd(request):
    
    return render(request, "cnx_user/mdp.html")



# Dash-home
@login_required(login_url='login')
def dash_home(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    # Récupérer les 8 premières catégories
    categories = Categorie.objects.all()[:8]
    
    # Préparer les données pour chaque catégorie
    categories_data = []
    for categorie in categories:
        # Compter le nombre de produits liés à la catégorie via les sous-catégories
        produits_count = sum([sous_categorie.produit_set.count() for sous_categorie in categorie.souscategorie_set.all()])
        
        categories_data.append({
            'categorie': categorie,
            'nombre_produits': produits_count,
        })

    context = {
        'categories_data': categories_data,
    }   
    
    return render(request, "DashAdmin/pg_acceuil.html", context) 

# Dash-customer
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customers(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    # Récupérer les paramètres de recherche
    code_recu = request.GET.get('code_recu', '')
    nom_client = request.GET.get('nom_client', '')
    nom_caissiere = request.GET.get('nom_caissiere', '')
    prix = request.GET.get('prix', '')
    date_verif = request.GET.get('date_verif', '')
    date_pay = request.GET.get('date_pay', '')
    
    tickets = Paiement.objects.all().order_by('-date')
    
    if code_recu:
        tickets = tickets.filter(code_verification__icontains=code_recu)
    if nom_client:
        tickets = tickets.filter(nom_du_client__icontains=nom_client)
    if nom_caissiere:
        tickets = tickets.filter(verifieur__icontains=nom_caissiere)
    if prix:
        tickets = tickets.filter(montant_paie=prix)
    if date_verif:
        tickets = tickets.filter(date_verif__date=date_verif)
    if date_pay:
        tickets = tickets.filter(date__date=date_pay)
    
    tickets_data = []
    
    for ticket in tickets:
        commandes = Commande.objects.filter(paiement=ticket)
        
        # Récupérer les détails de chaque produit de la commande
        produit_details = [{
            'produit_nom': commande.produit.nom_prod,
            'quantite': commande.quantite,
            'prix_unitaire': commande.prix_unitaire,
            'total': commande.prix_unitaire * commande.quantite,
            'date_expiration': commande.produit.date_peremption.strftime('%d-%m-%Y')
        } for commande in commandes]
        
        total_montant = ticket.montant_paie
        statut_paiement = "Payé" if ticket.etat_paie else "Non payé"
        statut_verification = "Vérifié" if ticket.verification else "Non vérifié"
        
        # Convertir `produit_details` en JSON
        produit_details_json = json.dumps(produit_details, default=str)
        
        # Ajouter les informations dans un dictionnaire
        ticket_info = {
            'ticket_code': ticket.code_verification,
            'nom_caissiere': ticket.verifieur,  # Caissière = l'utilisateur qui a fait le paiement
            'produit_details': produit_details_json,
            'total_montant': total_montant,
            'statut_paiement': statut_paiement,
            'statut_verification': statut_verification,
            'date_verif': ticket.date_verif,
            'date_pay': ticket.date,
            'nom_client': ticket.nom_du_client,
            'phone_client': ticket.phone,
            'methode_paiement': ticket.methode_paie,
            'tablette': ticket.user.username,            
        }
        tickets_data.append(ticket_info)
        
    return render(request, "DashAdmin/customers.html", {'tickets': tickets_data})

# Dash-Settings 
@login_required(login_url='login')
def settings_dash(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    user = request.user
    # Créer ou récupérer le profil
    profile, created = Profile.objects.get_or_create(user=user)  

    
    if request.method == 'POST':
        
        if 'pseudo' in request.POST and 'email' in request.POST and 'last_name' in request.POST and 'first_name' in request.POST:
            # Récupérer les données du formulaire
            pseudo = request.POST.get('pseudo')
            email = request.POST.get('email')
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name') 
            
            # Vérifier si le pseudo commence par une lettre
            if not re.match(r'^[a-zA-Z]', pseudo):
                messages.error(request, _("Le pseudo doit commencer par une lettre."), extra_tags='personal_info')
                return redirect('settings_dash')
            
            # Vérifier si le pseudo ou l'email a changé
            if pseudo == user.username and email == user.email and last_name == user.last_name and first_name == user.first_name:
                messages.info(request, _("Aucune modification apportée."), extra_tags='personal_info')
                return redirect('settings_dash')
            
            user.username = pseudo
            user.last_name = last_name
            user.first_name = first_name
            
            # Vérifier si l'email a changé et est unique
            if email != user.email:
                try:
                    user.email = email
                    user.full_clean()  # Valide les données de l'utilisateur
                except ValidationError:
                    messages.error(request, _("L'adresse e-mail est déjà utilisée ou invalide."), extra_tags='personal_info')
                    return redirect('settings_dash')
            
            # Enregistrer les modifications
            user.save()
            messages.success(request, _("Les modifications ont été enregistrées avec succès."), extra_tags='personal_info')
            return redirect('settings_dash')
        
        # Gestion du changement de mot de passe
        elif 'password' in request.POST and 'confirm-password' in request.POST:
            old_password = request.POST.get('last_password')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')

            # Vérification des champs de mot de passe
            if not old_password or not new_password or not confirm_password:
                messages.warning(request, _("Tous les champs de mot de passe doivent être remplis."), extra_tags='password_change')
                return redirect('settings_dash')
            
            # Vérifier que l'ancien mot de passe est correct
            if not user.check_password(old_password):
                messages.error(request, _("L'ancien mot de passe est incorrect."))
                return redirect('settings_dash')

            # Vérifier que les nouveaux mots de passe correspondent
            if new_password != confirm_password:
                messages.error(request, _("Les nouveaux mots de passe ne correspondent pas."), extra_tags='password_change')
                return redirect('settings_dash')

            # Vérifier si le nouveau mot de passe est identique à l'ancien
            if user.check_password(new_password):
                messages.info(request, _("Le nouveau mot de passe est identique à l'ancien mot de passe."), extra_tags='password_change')
                return redirect('settings_dash')

            # Mettre à jour le mot de passe
            user.set_password(new_password)
            user.save()

            # Maintenir la session après le changement de mot de passe
            update_session_auth_hash(request, user)
            
            messages.success(request, _("Le mot de passe a été changé avec succès."), extra_tags='password_change')
            return redirect('settings_dash')
        
        # Gestion de la modification de l'image de profil
        elif 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user.profile.profile_pic = profile_pic # Assure-toi que le champ profile_pic existe
            user.profile.save()
            messages.success(request, _("Image de profil modifiée avec succès."), extra_tags='personal_info')
            return redirect('settings_dash')
        
    return render(request, "DashAdmin/settings.html")


# Liste des Tablettes
@login_required(login_url='login')
def tablet_list(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    # Récupérer le groupe "tablettes"
    tablettes_group = Group.objects.get(name="tablette")
    # Récupérer les utilisateurs appartenant à ce groupe
    tablettes_users = User.objects.filter(groups=tablettes_group)
    
    # Passer les utilisateurs dans le contexte
    context = {
        'tablettes_users': tablettes_users,
    }
    
    return render(request, 'DashAdmin/tablette.html', context)

# Liste des Tablettes
@login_required(login_url='login')
def update_caiss(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    # Récupérer le groupe "tablettes"
    caissieres_group = Group.objects.get(name="caissiere")
    # Récupérer les utilisateurs appartenant à ce groupe
    caissieres_users = User.objects.filter(groups=caissieres_group)
    
    # Passer les utilisateurs dans le contexte
    context = {
        'caissieres_users': caissieres_users,
    }
    
    return render(request, 'DashAdmin/caissiere.html', context)


# Modif Tablette
@login_required(login_url='login')
def modifier_tablette(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    if request.method == 'POST':
        tablet_id = request.POST.get('tablet_id')
        new_password = request.POST.get('new_password')

        # Vérification des champs vides
        if not tablet_id or not new_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('update_tab')  # Remplace par le nom de ta page ou URL de redirection
        
        # Vérification des champs vides
        try:
            # Recherche de l'utilisateur avec l'ID fourni
            tablette = User.objects.get(id=tablet_id)
            
            # Vérification que l'utilisateur appartient au groupe "Tablette"
            groupe_tablette = Group.objects.get(name="tablette")
            if groupe_tablette in tablette.groups.all():
                # Modification du mot de passe après hachage
                tablette.password = make_password(new_password)
                tablette.save()
                messages.success(request, "Mot de passe modifié avec succès")
            else:
                # Message d'erreur si l'utilisateur n'est pas dans le groupe "Tablette"
                messages.warning(request, "Identifiants incorrects !")
        
        except User.DoesNotExist:
            # Message d'erreur si l'ID de tablette est introuvable
            messages.warning(request, "ID de tablette introuvable")
            
    return redirect('update_tab')


# Modif Tablette
@login_required(login_url='login')
def modifier_caiss(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    if request.method == 'POST':
        caiss_id = request.POST.get('caiss_id')
        new_password = request.POST.get('new_password')

        # Vérification des champs vides
        if not caiss_id or not new_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('update_caiss')  # Remplace par le nom de ta page ou URL de redirection
        
        # Vérification des champs vides
        try:
            # Recherche de l'utilisateur avec l'ID fourni
            caissiere = User.objects.get(id=caiss_id)
            
            # Vérification que l'utilisateur appartient au groupe "caissiere"
            groupe_caissiere = Group.objects.get(name="caissiere")
            if groupe_caissiere in caissiere.groups.all():
                # Modification du mot de passe après hachage
                caissiere.password = make_password(new_password)
                caissiere.save()
                messages.success(request, "Mot de passe modifié avec succès")
            else:
                # Message d'erreur si l'utilisateur n'est pas dans le groupe "Tablette"
                messages.warning(request, "Identifiants incorrects !")
        
        except User.DoesNotExist:
            # Message d'erreur si l'ID de tablette est introuvable
            messages.warning(request, "ID Caissiere introuvable")
            
    return redirect('update_caiss')


@login_required(login_url='login')
def import_csv(request):
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    if request.method == "POST":
        try:
            csv_file = request.FILES['products-csv']
            
            # Vérifier si c'est bien un fichier CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Le fichier doit être au format CSV")
                return redirect('add_products')
            
            # Lire le fichier CSV
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                code_barre = row.get('code_barre')
                nom_prod = row.get('nom_prod')
                date_fabrication = row.get('date_fabrication')
                date_peremption = row.get('date_peremption')
                quantite = row.get('quantite')
                prix = row.get('prix')

                # Créer le produit, les champs categorie et sous_categorie sont laissés vides
                Produit.objects.create(
                    code_barre=code_barre,
                    nom_prod=nom_prod,
                    date_fabrication=date_fabrication,
                    date_peremption=date_peremption,
                    quantite=quantite,
                    prix=prix,
                    fournisseur=row.get('fournisseur', ''),
                    emplacement_prod=row.get('emplacement_prod', '')
                )
                
            messages.success(request, "Les produits ont été importés avec succès.")
            return redirect('add_products')
        
        except Exception:
            messages.warning(request, "Veuillez charger un fichier valide")
            return redirect('add_products')
    
    return render(request, "DashAdmin/add_products.html")

@login_required(login_url='login')
def product(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    if request.method == "POST":
        nom_prod = request.POST.get('name')
        code_barre = request.POST.get('barcode')
        prix = request.POST.get('price')
        quantite = request.POST.get('quantity')
        date_fab = request.POST.get('date_fab')
        date_exp = request.POST.get('date_exp')
        fournisseur_id = request.POST.get('fournisseur')
        sous_categorie_id = request.POST.get('subcategory')

        try:
            # Créer un nouvel objet Produit
            Produit.objects.create(
                nom_prod=nom_prod,
                code_barre=code_barre,
                prix=prix,
                quantite=quantite,
                date_fabrication=date_fab,
                date_peremption=date_exp,
                fournisseur_id=fournisseur_id,
                sous_categorie_id=sous_categorie_id
            )
            messages.success(request, "Produit créé avec succès !") 
            return redirect('product')  
        except Exception:
            messages.error(request, f"Erreur lors de la création du produit ") 

    # Récupérer les fournisseurs et sous-catégories pour le formulaire
    fournisseur = Fournisseur.objects.all()
    sous_cat = SousCategorie.objects.all()

    return render(request, 'DashAdmin/product.html', {
        'fournisseurs': fournisseur,
        'sous_cats': sous_cat,
    }) 

# Fournisseur
@login_required(login_url='login')
def fournisseur(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('name')
        prenom = request.POST.get('first_name')
        adresse = request.POST.get('adress')
        numero_telephone = request.POST.get('number_tel')
                
        # Validation simple (tu peux ajouter plus de validation ici)
        if nom and prenom and numero_telephone:
            # Création d'un nouveau fournisseur
            fournisseur = Fournisseur(
                nom=nom,
                prenom=prenom,
                Adresse=adresse,
                numero_telephone=numero_telephone
            )
            fournisseur.save()
            
            # Message de succès
            messages.success(request, 'Le fournisseur a été ajouté avec succès.')
            return redirect('fourn')  # Redirection après l'ajout
        
        # Si des champs sont manquants
        else:
            messages.error(request, 'Veuillez remplir tous les champs requis.')
    return render(request, "DashAdmin/fournisseur.html")


@login_required(login_url='login')
def viewall(request):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    # Récupérer les catégories avec leur nom, la somme des produits, et l'image
    categories = Categorie.objects.all()
    
    # Préparer les données pour chaque catégorie
    categories_data = []
    for categorie in categories:
        # Compter le nombre de produits liés à la catégorie via les sous-catégories
        produits_count = sum([sous_categorie.produit_set.count() for sous_categorie in categorie.souscategorie_set.all()])
        
        categories_data.append({
            'categorie': categorie,
            'nombre_produits': produits_count,
        })
            
        context={
            'categories':categories_data
        }   
    return render(request, "DashAdmin/viewall.html", context) 

@login_required(login_url='login')
def detail_cat(request, categorie_id):
    # Vérifier si l'utilisateur appartient au groupe 'administrateur'
    if not request.user.groups.filter(name='administrateur').exists():
        return redirect('login')
    
    categorie = get_object_or_404(Categorie, id=categorie_id)
    sous_categories = categorie.souscategorie_set.all()

    sous_categorie_data = []
    total_produits = 0  # Variable pour stocker le nombre total de produits

    for sous_categorie in sous_categories:
        produits = sous_categorie.produit_set.all()
        nombre_produits = produits.count()
        total_produits += nombre_produits  # Ajouter le nombre de produits de chaque sous-catégorie au total
        
        sous_categorie_data.append({
            'sous_categorie': sous_categorie,
            'produits': produits,
            'nombre_produits': nombre_produits  
        })

    context = {
        'categorie': categorie,
        'sous_categorie_data': sous_categorie_data,
        'total_produits': total_produits
    }
    return render(request, "DashAdmin/detail_cat.html", context) 

def modif_info_user(request):
    return render(request, 'DashAdmin/modif_info_user.html')


# Caissiere home 
@login_required(login_url='login')
def search_by_code(request):
    # Vérifier si l'utilisateur appartient au groupe 'caissière'
    if not request.user.groups.filter(name='caissiere').exists():
        return redirect('login')
    
    try:
        del request.session['code_verif']
    except:
        pass 
    
    if request.method == 'POST':
        code_verification = request.POST.get('code_verification')

        try:            
            # Vérifier si un paiement correspondant existe
            paiement = Paiement.objects.get(code_verification=code_verification)
            
            # Vérifier l'état et le statut de vérification du paiement
            if not paiement.etat_paie:
                # Paiement échoué
                context = {
                    'error': "Le paiement du Client a échoué ."
                }
            
            elif paiement.verification:
                # Paiement déjà vérifié
                context = {
                    'error': "Ce paiement a déjà été vérifié."
                }
                
            else:  
            # Filtrer les commandes associées à ce Paiement valide et non vérifié
                commandes = Commande.objects.filter(user=paiement.user, paiement=paiement.id, paid=True, ordered=True)
                
                # Calculer la somme des quantités des commandes
                total_quantity = commandes.aggregate(Sum('quantite'))['quantite__sum'] or 0  # Utilise 0 comme valeur par défaut
                
                # Stocker le code de vérification dans la session pour l'utiliser dans la vue de génération du reçu
                request.session['code_verif'] = code_verification
                
                # Préparer les données pour le contexte
                context = {
                    'paiement': paiement,
                    'commandes': commandes,
                    'total_quantity': total_quantity
                }
        except Paiement.DoesNotExist:
            context = {
                'error': "Aucun paiement trouvé pour ce code de vérification.",
            }
        
        return render(request, 'Caissiere/index.html', context)
    
    return render(request, 'Caissiere/index.html')  

# Historique des vérifications
@login_required(login_url='login')
def caiss_history(request):   
    # Vérifier si l'utilisateur appartient au groupe 'caissière'
    if not request.user.groups.filter(name='caissiere').exists():
        return redirect('login')
         
    # Récupérer les paiements vérifiés par la caissière
    paiements = Paiement.objects.filter(
        verifieur=request.user.get_full_name(),
        verification=True,
        id_verifieur=request.user.id,
    ).order_by('-date')
        
    if request.method == 'GET':
        # Récupérer les paramètres de recherche depuis la requête GET
        code_recu = request.GET.get('code_recu', '').strip()
        nom_client = request.GET.get('nom_client', '').strip()
        nom_caissiere = request.GET.get('nom_caissiere', '').strip()
        prix = request.GET.get('prix', '').strip()
        date_verif = request.GET.get('date_verif', '').strip()
        date_pay = request.GET.get('date_pay', '').strip()
        
        
        # Appliquer les filtres dynamiquement en fonction des champs de recherche
        if code_recu:
            paiements = paiements.filter(code_verification__icontains=code_recu)
        
        if nom_client:
            paiements = paiements.filter(nom_du_client__icontains=nom_client)

        if nom_caissiere:
            paiements = paiements.filter(verifieur__icontains=nom_caissiere)
        
        if prix:
            paiements = paiements.filter(montant_paie=prix)

        if date_verif:
            paiements = paiements.filter(date_verif__date=date_verif)

        if date_pay:
            paiements = paiements.filter(date__date=date_pay)
        

    # Récupérer les commandes et produits liés à ces paiements
    commandes = []
    for paiement in paiements:
        # Récupérer les commandes liées à l'utilisateur qui a effectué le paiement
        commandes.extend(paiement.commande_set.all())

    # Passer les données au template
    context = {
        'paiements': paiements,
        'commandes': commandes,
    }

    return render(request, 'Caissiere/history.html', context)

# Afficher le reçu d'impression
@login_required(login_url='login')
def caiss_reçu(request):
    # Vérifier si l'utilisateur appartient au groupe 'caissière'
    if not request.user.groups.filter(name='caissiere').exists():
        return redirect('login')
    
    if not request.session.get('code_verif'):
        return redirect('caiss_home')
    # Récupérer le code de vérification depuis la session ou directement du paiement
    code_verification = request.session.get('code_verif', None)
    
    # Vérifier que le code de vérification est valide
    paiement = get_object_or_404(Paiement, code_verification=code_verification)

    # Récupérer les commandes associées à ce paiement
    commandes = Commande.objects.filter(user=paiement.user, paid=True, ordered=True, paiement=paiement.id)  # Assurez-vous que 'commandes' est une relation liée au modèle Paiement

    context = {
        'paiement': paiement,
        'commandes': commandes
    }
    return render(request, 'Caissiere/reçu.html', context)


# Valider la vérification de la caissiere
@login_required(login_url='login')
def caiss_verification(request, paiement_id):    
    # Vérifier si l'utilisateur appartient au groupe 'caissière'
    if not request.user.groups.filter(name='caissiere').exists():
        return redirect('login')
    
    if request.method == 'POST':
        try:
            paiement = Paiement.objects.get(id=paiement_id)
            paiement.verification = True
            paiement.verifieur = request.user.get_full_name() # ou username selon ce que tu préfères
            paiement.id_verifieur = request.user.id
            paiement.date_verif = timezone.now()
            paiement.save()
            return JsonResponse({'status': 'success'})
        except Paiement.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Paiement non trouvé.'})

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}) 


# Afficher les produits payés
@login_required(login_url='login')
def caiss_get_products(request, paiement_id):
    # Vérifier si l'utilisateur appartient au groupe 'caissière'
    if not request.user.groups.filter(name='caissiere').exists():
        return redirect('login')
    
    try:
        # Récupérer le paiement par son ID
        paiement = Paiement.objects.get(id=paiement_id)
        
        # Récupérer les commandes associées à l'utilisateur de ce paiement qui sont déjà payées
        commandes = Commande.objects.filter(user=paiement.user, paid=True, ordered=True, paiement=paiement.id)
        
        products = []
        # Parcourir les commandes et récupérer les détails des produits
        for commande in commandes:
            produit = commande.produit  # ForeignKey, donc chaque commande a un seul produit
            products.append({
                'nom': produit.nom_prod,
                'quantite': commande.quantite,
                'unite': commande.prix_unitaire,
                'total': commande.prix_unitaire * commande.quantite,  # Exemple de calcul du total
                'date_peremption': produit.date_peremption.strftime('%Y-%m-%d')
            })
        
        # Retourner les produits sous forme de JSON
        return JsonResponse({'products': products}, safe=False)
    
    except Paiement.DoesNotExist:
        return JsonResponse({'error': 'Paiement non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
