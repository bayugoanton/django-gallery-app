from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Album(models.Model):
    """
    Groups individual photos together. 
    The 'related_name' on the Photo model allows us to use 
    album.photos.all in our templates.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='albums/') # Ensure this exists
    # ... other fields
    
    # Track the creator of the album
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    
    is_admin_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class RecipePhoto(models.Model):
    """
    Stores individual recipe photos. 
    The ForeignKey links each photo to one specific Album.
    """
    # The 'related_name' is the key that enables the .photos.all loop
    album = models.ForeignKey(
        Album, 
        on_delete=models.CASCADE, 
        related_name='photos', 
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f"{self.title} (Album: {self.album.title if self.album else 'None'})"