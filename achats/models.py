from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Categorie
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.nom 
        
# Produit 
class Produit(models.Model):
    code_barre = models.CharField(max_length=30, unique=True)
    nom_prod = models.CharField(max_length=80)
    date_fabrication = models.DateField(null=True)
    date_peremption = models.DateField(null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    fournisseur = models.CharField(max_length=100, null=True, blank=True)
    emplacement_prod = models.CharField(max_length=60, blank=True)
    quantite = models.IntegerField()
    prix = models.FloatField()
    images = models.ImageField(upload_to='images', blank=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.nom_prod 
    
# Paiement
class Paiement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    montant_paie = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    methode_paie = models.CharField(max_length=50)
    etat_paie = models.BooleanField(default=False)
    ref_trans = models.CharField(max_length=60)
    code_verification = models.CharField(max_length=6, unique=True, default='000000')
    phone = models.IntegerField()
    nom_du_client = models.CharField(max_length=80)
    verification = models.BooleanField(default=False)
    verifieur = models.CharField(max_length=60, default='null')
    id_verifieur = models.CharField(max_length=15, default='null')

    class Meta:
        verbose_name = ("Paiement")
        verbose_name_plural = ("Paiements")
            
    def __str__(self):
        return f"Paiement de {self.montant_paie} par {self.user.username} - {self.ref_trans}"
    
# Commande 
class Commande(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False) 
    date_commande = models.DateTimeField(null=True, blank=True)

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
        
        for commande in self.commande.filter(ordered=False):
            # Produit commandé auparavant
            commande.ordered = True
            # L'heure de la suppresion
            commande.date_commande = timezone.now()
            commande.save()
            
        self.commande.clear()
        super().delete(*args, **kwargs)      
        

# Role des User
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('caissiere', 'Caissiere'),
        ('rayonniste', 'Rayonniste'),
        ('tablette', 'Tablette'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}" 