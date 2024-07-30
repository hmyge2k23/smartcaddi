from django.urls import path
from . import views

urlpatterns = [    
    path('', views.page_commander, name='commander'),
    
    # Ajout des Commandes au Panier
    path('AjoutPanier', views.AjoutPanier, name='ajout_panier'),
        
    # Transférer le Montant Total à L'API 
    path('Paiement', views.SendMontant, name='send_total'),
    
    # Supprimer une Commande spécifique
    path('DeleteCart', views.DeleteCart, name='del_cart'),
    
    # Vider le Panier
    path('DeleteCommande/<int:commande_id>', views.DeleteCommande, name='del_commande'),
    
    # Modifier la quantité d'une Commande 
    path('UpdateQuantity/', views.update_commande_quantity, name='update_commande_quantity'),
    
    # Paiement via API / Redirection vers Page Code Unique
    path('kkiapay/callback/', views.kkiapay_callback, name='kkiapay_callback'),
    
    # Paiement Succès
    path('Paiement/status/success/', views.payment_status, name='payment_status_success'),
    
    # Paiement Failed 
    path('Paiement/status/failed/', views.payment_status, name='payment_status_failed'),

    # Page contenant le Code de Vérification 
    path('Paiement/code_reçu_client', views.code_client, name='code_client'),
    
    # Supprimer les variables sessions (CodeUnique/Status)
    path('Paiement/DeleteVarSession', views.Delete_variable_session, name='delete_var_session'),
    
    
    # Vérification du Code par la caissière
    # path('Caissiere/Verification', views.verification_paiement, name='code_verif'),
    
]   

