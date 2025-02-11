from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Categorie
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    images = models.ImageField(upload_to='images/categories', blank=True)
    
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.nom 
        
# SousCategorie 
class SousCategorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "SousCategorie"
        verbose_name_plural = "SousCategories"

    def __str__(self):
        return self.nom

# Fournisseur 
class Fournisseur(models.Model):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=80)
    date_de_creation = models.DateTimeField(auto_now_add=True) 
    Adresse = models.CharField(max_length=60)
    numero_telephone = models.CharField(max_length=30)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom 

# Produit 
class Produit(models.Model):
    code_barre = models.CharField(max_length=30, unique=True)
    nom_prod = models.CharField(max_length=80)
    date_fabrication = models.DateTimeField(null=True)
    date_peremption = models.DateTimeField(null=True)
    sous_categorie = models.ForeignKey(SousCategorie, on_delete=models.SET_NULL, null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True) 
    emplacement_prod = models.CharField(max_length=60, blank=True)
    quantite = models.IntegerField()
    prix = models.FloatField()
    statut = models.CharField(max_length=20, default='Stock')

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        
    def save(self, *args, **kwargs):
        # Mise à jour automatique du statut en fonction de la quantité
        self.statut = 'Stock' if self.quantite > 0 else 'Rupture'
        super().save(*args, **kwargs)  # Appel à la méthode save() de la classe parente

    def __str__(self):
        return self.nom_prod     

# Paiement
class Paiement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    montant_paie = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    methode_paie = models.CharField(max_length=50)
    etat_paie = models.BooleanField(default=False)
    code_verification = models.CharField(max_length=6, unique=True, default='000000')
    phone = models.CharField(max_length=20)
    nom_du_client = models.CharField(max_length=80)
    verification = models.BooleanField(default=False)
    verifieur = models.CharField(max_length=60, default='null')
    id_verifieur = models.CharField(max_length=15, default='null')
    date_verif = models.DateTimeField(null=True)
    
    class Meta:
        verbose_name = ("Paiement")
        verbose_name_plural = ("Paiements")
            
    def __str__(self):
        return f"({self.code_verification}) par {self.user.username}"


# Commande 
class Commande(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False) 
    date_commande = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    paiement = models.ForeignKey(Paiement, on_delete=models.CASCADE, null=True, blank=True)  # Lien vers un paiement
    prix_unitaire = models.FloatField()

    class Meta:
        verbose_name = ('Commande')
        verbose_name_plural = ('Commandes')

    def __str__(self):
        return f"{self.produit} ({self.quantite})"
    
# Panier
class Panier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commande = models.ManyToManyField(Commande) 
    
    class Meta:
        verbose_name = ("Panier")
        verbose_name_plural = ("Paniers") 

    def __str__(self):
        return self.user.username 
    
    # Supprimer un produit commandé non acheté dans le Panier  
    def delete(self, *args, **kwargs):
        
        for commande in self.commande.filter(ordered=False, paid=False):
            # Produit retiré (Commandé auparavant)
            commande.ordered = True
            # L'heure de la suppresion
            commande.date_commande = timezone.now()
            commande.save()
            
        self.commande.clear()
        super().delete(*args, **kwargs)      
        
# Gestion des Images User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='images/admin_profil', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
        
# Historique de Paiement
class HistoriquePaiement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Lien vers l'utilisateur
    code_verification = models.CharField(max_length=50, unique=True)  # Code unique pour la transaction
    qr_image = models.CharField(max_length=50, unique=True)  # Chemin de l'image QR
    date_paiement = models.DateTimeField(auto_now_add=True)  # Date du paiement

    def __str__(self):
        return f"Paiement {self.code_verification} - {self.user.username}"