# Generated by Django 5.0.6 on 2024-07-03 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achats', '0005_alter_paiement_date_alter_paiement_etat_paie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
