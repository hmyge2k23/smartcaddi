# Generated by Django 5.0.6 on 2024-06-27 21:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Categorie',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField(default=1)),
                ('ordered', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Commande',
                'verbose_name_plural': 'Commandes',
            },
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_paie', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('methode_paie', models.IntegerField()),
                ('etat_paie', models.IntegerField()),
                ('ref_trans', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Paiement',
                'verbose_name_plural': 'Paiements',
            },
        ),
        migrations.CreateModel(
            name='Panier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('date_commande', models.DateTimeField(null=True)),
                ('commande', models.ManyToManyField(to='achats.commande')),
            ],
            options={
                'verbose_name': 'Panier',
                'verbose_name_plural': 'Paniers',
            },
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant', models.CharField(max_length=30, unique=True)),
                ('nom_prod', models.CharField(max_length=80)),
                ('date_fabrication', models.DateField(null=True)),
                ('date_peremption', models.DateField(null=True)),
                ('emplacement_prod', models.CharField(blank=True, max_length=60)),
                ('quantite', models.IntegerField()),
                ('prix', models.FloatField()),
                ('images', models.ImageField(blank=True, upload_to='images')),
                ('etat', models.CharField(choices=[('stock', 'Stock'), ('achat', 'Achat')], default='stock', max_length=20)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='achats.categorie')),
            ],
            options={
                'verbose_name': 'Produit',
                'verbose_name_plural': 'Produits',
            },
        ),
        migrations.AddField(
            model_name='commande',
            name='produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='achats.produit'),
        ),
        migrations.CreateModel(
            name='SousCategorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('categorie_parente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fk_Categorie', to='achats.categorie')),
            ],
            options={
                'verbose_name': 'Sous-catégorie',
                'verbose_name_plural': 'Sous-catégories',
            },
        ),
        migrations.AddField(
            model_name='produit',
            name='sous_categorie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='achats.souscategorie'),
        ),
    ]
