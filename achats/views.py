from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from achats.models import Commande, Panier, Produit, Paiement 
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from kkiapay import Kkiapay
import random
import string 
import qrcode
from io import BytesIO
import base64
from django.conf import settings
import os


# Page Acceuil 
def page_acceuil(request):
    if request.user.is_authenticated: 
        user_name = request.user.username
        return render(request, 'index.html', {'user_name':user_name})
    return render(request, 'index.html')


# Page Commander 
def page_commander(request):
    if request.user.is_authenticated: 
        try:
            panier = Panier.objects.get(user=request.user)
            # # Filtrer les commandes du Panier non payées
            commandes = panier.commande.filter(ordered=False)
            context ={
                'commandes':commandes
            }
            return render(request, 'cart.html', context)
         
        except Panier.DoesNotExist:
            # Panier non trouvé
            return render(request, 'cart.html', {'commandes': None})
    else:
        return render(request, 'cart.html')
    
            
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
        total_amount = request.POST.get('to')
        if is_valid_positive_float(total_amount):
            return render(request, "paiement/payment.html", {'total_amount': total_amount})

    return redirect('commander') 


# Commander un/des Produits  
def AjoutPanier(request):
    if request.method == 'POST':
        slug = request.POST.get('decodedText')
        # Recuperer le produit
        produit = get_object_or_404(Produit, code_barre=slug)
        # Recuperer/Creer le panier et la commande du user
        panier, _ = Panier.objects.get_or_create(user=request.user) 
        commande, created = Commande.objects.get_or_create(user=request.user, produit=produit, ordered=False) 
            
        # Si la commande est créé l'Ajouter au Panier
        if created:
            panier.commande.add(commande)
            panier.save()
        else:
            commande.quantite += 1
            commande.save() 
        return JsonResponse({'message': 'commande enregistré'})
    
    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


# Vider le Panier / Marqué les Commandes non Achetées 
def DeleteCart(request):    
    # Vérifie si (request.user.cart) Existe et l'affecter à cart
    if cart:= Panier.objects.get(user=request.user):
        cart.delete()  
    return redirect('commander')


# Supprimer une Commande Spécifique 
def DeleteCommande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, user=request.user, ordered=False)
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
        commande = Commande.objects.get(id=commande_id, ordered=False)
        # Mettre à jour la quantité de la commande
        commande.quantite = quantity
        commande.save()
        
        # Recalculer le prix total
        total_price = commande.produit.prix * quantity 
        
        return JsonResponse({
            'status': 'success',
            'total_price': total_price,
        })
    except Commande.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Commande non trouvée'}, status=404)
    

# Génération du code unique
def generate_unique_code(): 
    while True:
        digits_part = ''.join(random.choices(string.digits, k=5))
        letter_part = ''.join(random.choices(string.ascii_uppercase, k=1))
        code = digits_part + letter_part
        
        if not Paiement.objects.filter(code_verification=code).exists():
            return code
    
# Instance de Kkiapay
kkiapay_instance = Kkiapay(
    '37461a30244111efa4d6f74ba7c319a6',
    'tpk_37461a32244111efa4d6f74ba7c319a6',
    'tsk_37461a33244111efa4d6f74ba7c319a6',
    sandbox=True  
)

# Enregistrement du Paiement / Redirection       
@csrf_exempt
def kkiapay_callback(request):
    if request.method == 'GET':
        
        transaction_id = request.GET.get('transaction_id')
        user = User.objects.get(id=request.user.id)  
                                
        # Vérifie la transaction avec Kkiapay
        transaction = kkiapay_instance.verify_transaction(transaction_id)
        if transaction.get('status') == 'SUCCESS': 
            montant = transaction.get('amount')
            methode = transaction.get('source_common_name')
            date_paie = transaction.get('performed_at')
            
            client = transaction.get('client', {})
            phone_paie = client.get('phone')
            nom_du_client = client.get('fullname')
            etat = True  # Par exemple, 1 pour succès
            
            # Génère un code de vérification unique
            code_verification = generate_unique_code()  
        
            # Enregistre les informations de paiement dans la base de données
            paiement = Paiement(
                user=user, 
                montant_paie=montant,
                date=date_paie,
                methode_paie=methode, 
                etat_paie=etat, 
                ref_trans=transaction_id, 
                code_verification=code_verification, 
                phone = phone_paie,
                nom_du_client = nom_du_client
            )
            paiement.save()
            
            # Marquer les commandes associées comme payées
            commandes_non_payees = Commande.objects.filter(user=user, ordered=False, paid=False)
            for commande in commandes_non_payees:
                # La commande est maintenant payée
                commande.paid = True
                commande.save() 
            
            # Supprimer le panier de l'utilisateur
            try: 
                panier = Panier.objects.get(user=user)
                panier.delete()
            except Panier.DoesNotExist:
                pass 
            
            # Générer le code QR et le sauvegarder
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(code_verification)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            
            img_filename = f"qr_{code_verification}.png"
            img_path = os.path.join(settings.MEDIA_ROOT, img_filename)
            img.save(img_path)
            
            # variables session 
            request.session['code_verification'] = code_verification
            request.session['status'] = 'success'
            request.session['qr_image_url'] = settings.MEDIA_URL + img_filename
    
            # Rediriger l'utilisateur vers une page avec le code de vérification
            return redirect('payment_status_success')
        
        # Stocker l'échec dans la session
        request.session['status'] = 'failed'
        return redirect('payment_status_failed')       

    return render(request, 'error/400.html', status=404)

# Statut du paiement
def payment_status(request):
    code_verification = request.session.get('code_verification')
    status = request.session.get('status')
    
    if status == 'success':
        context = {
            'code_verification': code_verification,
            'status': status 
        }
    else:
        context = {'status': status}
        
    return render(request, 'paiement/payment_status.html', context) 

# Supprimer les 2 variables sessions (Code unique/status)
def Delete_variable_session(request):
        
    # Supprimer les variables de session après utilisation
    if 'code_verification' in request.session:
        del request.session['code_verification']
    if 'status' in request.session:
        del request.session['status']

    return redirect('commander')

# Code du Reçu Client 
def code_client(request):
    print(request.session.get('code_verification'))
    code_verification = request.session.get('code_verification')
    status = request.session.get('status')
    
    if code_verification and status=='success': 
        context = {'code_reçu': code_verification, 'status': status}
        return render(request, 'paiement/code_reçu_client.html', context)
    else:
        # Gérer le cas où codeVerification n'est pas disponible dans la session
        return render(request, 'error/404.html', status=404)


# Verification Caissière
# def verification_paiement(request):
#     if request.method == 'POST':
#         code_verification = request.POST.get('code_verification')
#         # Filtrer les paiements en utilisant le code de vérification
#         paiements = Paiement.objects.filter(code_verification=code_verification)
#         # les commandes associées aux paiements trouvés
#         commandes = Commande.objects.filter(paiement__in=paiements)
        
#         context = {
#             'paiements': paiements,
#             'commandes': commandes,
#             'code_verification': code_verification,
#         }
#         return render(request, 'verification.html', context)
    
#     return render(request, 'verification.html') 

