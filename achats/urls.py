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
    
    # CallBack API / Redirection vers Page Code Unique
    path('ApiPay/callback', views.payement, name='api_pay'),
    
    # Paiement Succès / Failed
    path('Paiement/status', views.payment_status, name='payment_status'),
    
    # # Paiement  
    # path('Paiement/status/failed/', views.payment_status, name='payment_status_failed'),

    # Page contenant le Code de Vérification 
    path('Paiement/code_reçu_client', views.code_client, name='code_client'),
    
    # Supprimer les variables sessions (CodeUnique/Status)
    path('Paiement/DeleteVarSession', views.Delete_variable_session, name='delete_var_session'),
    
    path('Paiement/historique', views.dernier_pay, name='dernier_pay'),    
]   