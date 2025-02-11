from django.urls import path
from . import views

urlpatterns = [    
    # Connsion User (tablette, caissiere, Admin)
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutPage, name='logout'),
    path('reset', views.reset_pwd, name='reset_pwd'),
    
    
    # DashAdmin
        path('DashAdmin/', views.dash_home ,name='dash_home'),
        
        path('DashAdmin/customers', views.customers ,name='customers'),
        
        path('DashAdmin/settings', views.settings_dash ,name='settings_dash'),

        path('DashAdmin/viewall', views.viewall ,name='viewall'),
        
        path('DashAdmin/add_products', views.import_csv ,name='add_products'),
        
        path('DashAdmin/product', views.product ,name='product'),
        
        path('DashAdmin/fournisseur', views.fournisseur ,name='fourn'),
        
        path('DashAdmin/detail_cat/<int:categorie_id>/', views.detail_cat ,name='detail_cat'),
        
        path('DashAdmin/modif_user', views.modif_info_user ,name='modif_info_user'),
        
        path('DashAdmin/Update/Tablette', views.tablet_list ,name='update_tab'),
        
        path('DashAdmin/Update/ModifTab', views.modifier_tablette ,name='modifier_tab'),
        
        path('DashAdmin/Update/ModifCaiss', views.modifier_caiss ,name='modifier_caiss'),
        
        path('DashAdmin/Update/Caissiere', views.update_caiss ,name='update_caiss'),
           
               
    # Caissiere
        path('Caissiere/', views.search_by_code ,name='caiss_home'),
        
        path('Caissiere/history', views.caiss_history ,name='caiss_history'),
        
        path('Caissiere/reçu', views.caiss_reçu ,name='caiss_reçu'),
                
        path('Caissiere/update_verif/<int:paiement_id>/', views.caiss_verification, name='update_verif'),
        
        path('Caissiere/get_products/<int:paiement_id>/', views.caiss_get_products, name='caiss_get_products')
]