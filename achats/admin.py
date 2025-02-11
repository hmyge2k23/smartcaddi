from django.contrib import admin
from .models import Paiement, Panier, Produit, Categorie, Commande, SousCategorie, Fournisseur, Profile, HistoriquePaiement


# Produit
class AdminProduit(admin.ModelAdmin):
    list_display = ("code_barre", "nom_prod", "quantite", "prix", "emplacement_prod", "fournisseur", "sous_categorie", "statut")
    
admin.site.register(Produit, AdminProduit)

# Profil images_admin
class AdminProfile(admin.ModelAdmin):
    list_display = ("user", "profile_pic")
    
admin.site.register(Profile, AdminProfile)

# Fournisseur
class AdminFournisseur(admin.ModelAdmin):
    list_display = ("nom", "prenom", "Adresse", "date_de_creation", "numero_telephone")
    
admin.site.register(Fournisseur, AdminFournisseur)

# Categorie
class AdminCategorie(admin.ModelAdmin):
    list_display = ("nom", "description", "images") 
    
admin.site.register(Categorie, AdminCategorie)

# SousCategorie
class AdminSousCategorie(admin.ModelAdmin):
    list_display = ("nom", "description", "categorie", 'categorie') 
    
admin.site.register(SousCategorie, AdminSousCategorie)

# Commande
class AdminCommande(admin.ModelAdmin):
    list_display = ("produit", "user", "quantite", "date_commande", "ordered", "paid", "prix_unitaire", "paiement")
    
admin.site.register(Commande, AdminCommande)

# Panier
class AdminPanier(admin.ModelAdmin):
    list_display =("user",)
    
admin.site.register(Panier,AdminPanier)

# Paiement
class AdminPaiement(admin.ModelAdmin):
    list_display =("user", "montant_paie", "methode_paie", "date", "code_verification", "nom_du_client", "phone", "etat_paie", "verification","id_verifieur", "verifieur", "date_verif")
    
admin.site.register(Paiement,AdminPaiement)      


# Historique Paiement
class HistoriquePay(admin.ModelAdmin):
    list_display =("user", "code_verification", "date_paiement", "qr_image")
    
admin.site.register(HistoriquePaiement, HistoriquePay)