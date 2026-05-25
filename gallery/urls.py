from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Authentication Routes ---
    # Using Django's built-in auth views for security and standard session handling
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    
    # Custom sign-up route
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),

    # --- Gallery Workspace Routes ---
    # Home/Dashboard: Shows all available albums
    path('', views.AlbumListView.as_view(), name='album_list'),
    
    # Detail View: The page that shows specific photos inside an album
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    
    # Creation: Add a new album container
    path('album/new/', views.AlbumCreateView.as_view(), name='album_create'),
    
    # Upload: Add photos specifically to an album (note the <int:album_id>)
    path('album/<int:album_id>/upload/', views.PhotoCreateView.as_view(), name='photo_create'),
    
    # Modification: Edit or remove existing photos
    path('photo/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo_edit'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]