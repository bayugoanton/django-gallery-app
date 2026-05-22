from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
import cloudinary.uploader
import logging
from .models import Album, RecipePhoto

# Setup logger for production debugging
logger = logging.getLogger(__name__)

# --- ACCOUNT REGISTRATION ---
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Account created successfully! Please log in.")
        return super().form_valid(form)

# --- ALBUM MANAGEMENT ---
class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'gallery/album_list.html'
    context_object_name = 'albums'
    paginate_by = 6

    def get_queryset(self):
        # Admins see everything; users see non-admin-only albums
        if self.request.user.is_staff:
            return Album.objects.all().order_by('-created_at')
        return Album.objects.filter(is_admin_only=False).order_by('-created_at')

class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        # Optimize query: filter photos belonging to this album
        photos = self.object.photos.all().order_by('-uploaded_at')
        
        if query:
            photos = photos.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            
        context['photos'] = photos
        context['query'] = query
        return context

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    fields = ['title', 'description', 'is_admin_only']
    template_name = 'gallery/album_form.html'
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Album created successfully.")
        return super().form_valid(form)

# --- PHOTO CRUD OPERATIONS ---
class PhotoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RecipePhoto
    fields = ['title', 'description', 'image']
    template_name = 'gallery/photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Fetch album first to validate permissions early
        self.album = get_object_or_404(Album, pk=self.kwargs['album_id'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.album.created_by == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        form.instance.album = self.album
        messages.success(self.request, "Recipe photo uploaded successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.album.pk})

class PhotoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RecipePhoto
    fields = ['title', 'description']
    template_name = 'gallery/edit.html'
    context_object_name = 'photo'

    def test_func(self):
        return self.get_object().album.created_by == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "Recipe details updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album.pk})

class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = RecipePhoto
    template_name = 'gallery/delete.html'
    context_object_name = 'photo'

    def test_func(self):
        return self.get_object().album.created_by == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        photo = self.get_object()
        try:
            if photo.image:
                cloudinary.uploader.destroy(photo.image.public_id)
            messages.success(self.request, "Photo deleted successfully.")
        except Exception as e:
            logger.error(f"Cloudinary deletion error: {e}")
            messages.error(self.request, "Photo record removed, but image deletion failed.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album.pk})