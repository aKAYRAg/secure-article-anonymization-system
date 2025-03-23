from django.db import models
from user.models import User
from article.models import Article
from .utils import decrypt_aes_key_with_private_key, encrypt_aes_key_with_rsa

class FileAccessManager(models.Manager):

    def create_file_access(self, article, user_owned, user_access):

        # Kullanıcıya ait AES anahtarını çöz
        aes_key_decrypt = decrypt_aes_key_with_private_key(
            article.aes_key_enc,  # article.aes_key_enc() yerine article.aes_key_enc
            user_owned.get_rsa_private_key()
        )

        # Kullanıcının AES anahtarını yeniden şifrele
        aes_key_encrypt = encrypt_aes_key_with_rsa(
            aes_key_decrypt,
            user_access.get_rsa_public_key()
        )

        # Yeni dosya erişim kaydını oluştur
        file_access = self.create(
            file=article,         # Makale nesnesi
            user=user_access,     # Kullanıcı nesnesi
            aes_key_enc=aes_key_encrypt,  # Şifreli AES anahtarı
        )
        return file_access


class FileAccess(models.Model):
    """
    Kullanıcıların belirli dosyalara erişim haklarını temsil eden model.
    """
    file = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    aes_key_enc = models.TextField(null=True, blank=True)
    iv = models.TextField(null=True, blank=True)

    objects = FileAccessManager()  # Özel model yöneticisi atanıyor.

    def __str__(self):
        return f"{self.user} -> {self.file}"  # Kullanıcıdan makaleye erişim şeklinde gösterim
