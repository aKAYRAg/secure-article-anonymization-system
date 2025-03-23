from django.db import models
from user.models import User
import base64

# Create your models here.

class Article(models.Model):

    makale_adi = models.CharField(max_length=255)

    # Makale orijinal dosyası
    makale_orjinal_path = models.FileField(upload_to='makaleler/orjinal/', blank=False, null=False)

    # Makale anonim dosyası
    makale_anonim_path = models.FileField(upload_to='makaleler/anonim/', blank=True, null=True)

    # Makale yanıtlı dosyası
    makale_yanitli_path = models.FileField(upload_to='makaleler/yanitli/', blank=True, null=True)

    # Makale oluşturulma tarihi ve saati
    makale_tarih = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,related_name="owned_articles")

    hakem = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_articles")

    aes_key_enc = models.TextField(null=True, blank=True)

    iv = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.makale_adi
    
    
        
    def get_aes_key_enc(self):
        return self.aes_key_enc

    def get_iv(self):
        return self.iv