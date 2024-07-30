from django.contrib import admin
from .models import Paiement, Panier, Produit, Categorie, Commande
from .models import UserProfile

# Produit
class AdminProduit(admin.ModelAdmin):
    list_display = ("code_barre", "nom_prod", "quantite", "prix", "categorie", "emplacement_prod", "images")
    
admin.site.register(Produit, AdminProduit)

# Categorie
class AdminCategorie(admin.ModelAdmin):
    list_display = ("nom", "description") 
    
admin.site.register(Categorie, AdminCategorie)

# Commande
class AdminCommande(admin.ModelAdmin):
    list_display = ("produit", "user", "quantite", "date_commande", "ordered", "paid")
    
admin.site.register(Commande, AdminCommande)

# Panier
class AdminPanier(admin.ModelAdmin):
    list_display =("user",)
    
admin.site.register(Panier,AdminPanier)

# Paiement
class AdminPaiement(admin.ModelAdmin):
    list_display =("user", "montant_paie", "methode_paie", "date", "ref_trans", "code_verification", "nom_du_client", "phone", "etat_paie", "verification","id_verifieur", "verifieur")
    
admin.site.register(Paiement,AdminPaiement)      

# Model User Personnalisé
class AdminUser(admin.ModelAdmin):
    list_display =("user", "role")
admin.site.register(UserProfile, AdminUser)