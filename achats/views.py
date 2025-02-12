from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from achats.models import Commande, Panier, Produit, Paiement, HistoriquePaiement
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import random
import string 
import qrcode
from django.conf import settings
import os
from kkiapay import Kkiapay
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.files import File

import logging
logger = logging.getLogger(__name__)


# Page Acceuil 
def page_acceuil(request):
    user_group = False
    
    if request.user.is_authenticated: 
        user_group = request.user.groups.filter(name='tablette').exists()
        user_name = request.user.username
        
        return render(request, 'index.html',{
            'user_name':user_name,
            'user_group': user_group
        })
        
    return render(request, 'index.html')


# Page Commander 
def page_commander(request):
    user_group = False
    
    if request.user.is_authenticated: 
        # Vérifier si l'utilisateur appartient au groupe 'tablette'
        user_group = request.user.groups.filter(name='tablette').exists()

        try:
            panier = Panier.objects.get(user=request.user)
            # Filtrer les commandes du Panier non payées
            commandes = panier.commande.filter(ordered=False, paid=False)
                        
        except Panier.DoesNotExist:
            commandes = None  # Pas de panier ni de commandes

        context = {
            'commandes': commandes,
            'user_group': user_group  # Toujours inclure user_group dans le contexte
        }
        return render(request, 'cart.html', context)
    
    else:
        return render(request, 'cart.html', {'user_group': user_group})
    
    
# Fonciton de vérification du Montant Total
def is_valid_positive_float(value):
    try:
        float_value = float(value)
        return float_value > 0
    except ValueError:
        return False 
  
# Transférer le Montant à L'API  
def SendMontant(request):
    if request.method == 'POST':
        total_amount = float(request.POST.get('to')) + float(request.POST.get('to')) * 0.013
        
        if is_valid_positive_float(total_amount):
            return HttpResponse("Erreur sur la fonction SendMontant")

    return redirect('commander')      


# Commander un/des Produits  
def AjoutPanier(request):
    if request.method == 'POST':
        slug = request.POST.get('decodedText')
    
        try:
            # Recuperer le produit
            produit = Produit.objects.get(code_barre=slug)
            
            # Vérifier le statut du produit
            if produit.statut == 'Rupture':
                return JsonResponse({'message': 'Article actuellement Indisponible.'}, status=400)
            
            # Recuperer/Creer le panier et la commande du user
            panier, _ = Panier.objects.get_or_create(user=request.user) 
            commande, created = Commande.objects.get_or_create(
                user=request.user,
                produit=produit,
                ordered=False,
                paid=False,
                defaults={'prix_unitaire': produit.prix}
                ) 
            
            # Si la commande est nouvelle l'Ajouter au Panier
            if created:
                commande.quantite = 1
                # commande.prix_unitaire = produit.prix
                panier.commande.add(commande)
            else:
                commande.quantite += 1
        
                   
            # Vérifier après chaque scanne si La Qté dans la commande ne dépasse pas celle du Produit         
            if commande.quantite > produit.quantite:
                # Diminuer le Surplus et Affiché le message d'erreur 
                commande.quantite -= 1
                commande.save() 
                return JsonResponse({'message': '⚠️ Y a plus de stock oooh!'}, status=400)
                      
            commande.save() 
            panier.save()  
            
            return JsonResponse({'message': 'commande enregistré'})
        
        except Produit.DoesNotExist:
            # Si le produit n'est pas trouvé dans la BD
            return JsonResponse({'message': 'Article non Trouvé !'}, status=404)
    
    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


# Vider le Panier / Marqué les Commandes non Achetées 
def DeleteCart(request):    
    # Vérifie si (request.user.cart) Existe et l'affecter à cart
    if cart:= Panier.objects.get(user=request.user):
        cart.delete()  
    return redirect('commander')


# Supprimer une Commande Spécifique 
def DeleteCommande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, user=request.user, ordered=False, paid=False)
    panier = Panier.objects.get(user=request.user)
    
    # Marquer la commande comme supprimée
    commande.ordered = True
    commande.date_commande = timezone.now()
    commande.save()

    # Supprimer la commande du panier
    panier.commande.remove(commande)

    # Si le panier est vide, le supprimer
    if not panier.commande.exists():
        panier.delete()
    
    return redirect('commander')


# Modifier la Quantité d'une Commande 
@require_POST
def update_commande_quantity(request):
    commande_id = request.POST.get('commande_id')
    quantity = int(request.POST.get('quantity'))
    try:
        commande = Commande.objects.get(id=commande_id, ordered=False, paid=False)
        # Mettre à jour la quantité de la commande
        commande.quantite = quantity
        commande.date_commande = timezone.now()
        commande.save()
        
        # Recalculer le prix total
        total_price = commande.prix_unitaire * quantity 
        
        return JsonResponse({
            'status': 'success',
            'total_price': total_price,
        })
    except Commande.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Commande non trouvée'}, status=404)
    

# Génération du code unique
def generate_unique_code(): 
    while True:
        digits_part = ''.join(random.choices(string.digits, k=3))
        letter_part = ''.join(random.choices(string.ascii_uppercase, k=1))
        code = digits_part + letter_part
        
        if not Paiement.objects.filter(code_verification=code).exists():
            return code
    
    
# Enregistrement du Paiement / Redirection  
@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)     
def payement(request):
    # Verifier si l'utilisateur est connecté
    logger.info(f"Session active: {request.user.is_authenticated}")
    if request.method == 'GET':
        
        transaction_id = request.GET.get('transaction_id')
        # Initialiser l'instance de Kkiapay
        k = Kkiapay('ff8048f0421b2a9d253146de1fec0432725d213a', 'pk_a2d4f2f910bb51055df4f14fa9d53da119a12d9a03e93e0fbd3005b22c70b51e', 'sk_61bba4269c522dc5bed5038a03de938e95028e0196a0c1139acf04b0ec0060ee', sandbox=False)
        
        # Vérifier la transaction
        transaction = k.verify_transaction(transaction_id)
        
        code_verification = generate_unique_code()
        
        
        if transaction_id:
            
            if transaction['status'] == 'SUCCESS':
                try:
                    client_info = transaction['client']
                    montant_paie = transaction['amount']
                    
                    
                    # Enregistrer le paiement réussi
                    paiement = Paiement(
                        user=request.user,
                        phone=client_info['phone'],
                        code_verification=code_verification,
                        nom_du_client=client_info['fullname'],
                        montant_paie=montant_paie,
                        methode_paie=transaction['source_common_name'],
                        date=timezone.now(),
                        etat_paie=True
                    )
                    paiement.save()
                    
                    # Marquer les commandes associées comme payées
                    commandes_non_payees = Commande.objects.filter(user=request.user, ordered=False, paid=False)
                    for commande in commandes_non_payees:
                        produit = commande.produit
                        if produit.quantite >= commande.quantite:
                            # Réduire la quantité du produit
                            produit.quantite -= commande.quantite  
                            produit.save()
                            commande.paid = True
                            commande.ordered = True
                            commande.paiement = paiement
                            commande.save()
                        else:
                            print(f"Stock insuffisant pour le produit {produit.nom_prod}")
                            
                    # Supprimer le panier de l'utilisateur
                    Panier.objects.filter(user=request.user).delete()
                    
                    # Générer le code QR et l'enregistrer
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(code_verification)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    
                    # Définir le chemin vers le dossier qr_codes
                    qr_folder = os.path.join(settings.MEDIA_ROOT, 'images', 'qr_codes')
                    os.makedirs(qr_folder, exist_ok=True)
                    
                    # Enregistrer l'image QR avec le chemin complet
                    img_filename = f"qr_{code_verification}.png"
                    img_path = os.path.join(qr_folder, img_filename)
                    img.save(img_path)
                    
                    # Ouvrir l'image comme un fichier pour l'attacher à `ImageField`
                    historique_paiement = HistoriquePaiement(
                        user = request.user,
                        code_verification = code_verification,
                        qr_image= settings.MEDIA_URL + 'images/qr_codes/' + img_filename
                    )
                    historique_paiement.save()
                                        
                    # Variables de session pour la redirection
                    request.session['code_verification'] = code_verification
                    request.session['status'] = 'success'
                    request.session['qr_image_url'] = settings.MEDIA_URL + 'images/qr_codes/' + img_filename
                    
                    
                    # Rediriger vers la page de succès
                    return redirect('payment_status')
                
                except Exception:
                    return render(request, 'error/400.html') # JsonResponse({'status': 'failed', 'error': str(e)}, status=400)
            
            else:
                try:
                    # Enregistrer le paiement comme échoué
                    paiement = Paiement(
                        user=request.user,
                        code_verification=code_verification,
                        etat_paie=False,
                        date=timezone.now(),
                        methode_paie=transaction['source_common_name']
                    )
                    paiement.save()
                    
                    # Définir les variables de session pour l'échec
                    request.session['status'] = 'failed'
                    
                    # Rediriger vers la page d'échec
                    return redirect('payment_status')
                    
                except Exception as e:    
                    return render(request, 'error/400.html') # JsonResponse({'status': 'failed', 'error': str(e)}, status=400)
        
        else:
            return render(request, 'error/400.html')
            
    return JsonResponse({'status': 'failed', 'error': "Méthode non autorisée"}, status=405)

    
# Statut du paiement
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def payment_status(request):
    
    # Vérification si l'utilisateur est toujours authentifié
    if not request.user.is_authenticated:
        logger.warning(f"Utilisateur déconnecté avant le callback: {request.user}")
        return redirect('login')  # Ou afficher une page d'erreur personnalisée

    
    code_verification = request.session.get('code_verification')
    status = request.session.get('status')
    qr_image_url = request.session.get('qr_image_url')
    
    if code_verification and code_verification and qr_image_url :
    
        if status == 'success' and code_verification and qr_image_url:
            context = {
                'code_verification': code_verification,
                'status': status
            }
        else:
            context = {
                'status': status
            }
    else:
        return render(request, 'error/404.html', status=404)
        
    return render(request, 'paiement/payment_status.html', context) 

# Supprimer les 2 variables sessions (Code unique/status)
def Delete_variable_session(request):
    # Supprimer les variables de session après utilisation
    if 'code_verification' in request.session:
        del request.session['code_verification']
    if 'status' in request.session:
        del request.session['status']
    if 'qr_image_url' in request.session:
        del request.session['qr_image_url']
        
    return redirect('commander') 

# Code de verification du Reçu Client
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def code_client(request):
    code_verification = request.session.get('code_verification')
    status = request.session.get('status')
    
    if code_verification and status=='success': 
        context = {'code_reçu': code_verification, 'status': status}
        return render(request, 'paiement/code_reçu_client.html', context)
    else:
        # Gérer le cas où codeVerification n'est pas disponible dans la session
        return render(request, 'error/404.html', status=404)


# Code de verification du Reçu Client
@login_required(login_url='login')  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dernier_pay(request):
    try:
        # Récupérer le dernier historique de paiement de l'utilisateur connecté
        history = HistoriquePaiement.objects.filter(user=request.user).latest('date_paiement')
    except HistoriquePaiement.DoesNotExist:
        # Si aucun historique de paiement n'est trouvé pour cet utilisateur
        history = None
    
    context={
        'history':history
    }
    return render(request, 'paiement/dernier_reçu.html', context)