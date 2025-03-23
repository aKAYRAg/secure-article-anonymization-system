from django import forms
from django.core.validators import RegexValidator
from django.conf import settings
from article.models import Article
from user.models import User
from sifreleme.utils import encrypt_pdf_with_rsa
from sifreleme.models import FileAccess
import os

class ArticleForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=255,
        required=True,
        label="E-mail",
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                message="Geçersiz e-posta formatı.",
            )
        ],
    )

    # Kullanıcıdan PDF dosyasını almak için FileField ekliyoruz
    makale_orjinal_path = forms.FileField(
        required=True,
        label="PDF Dosyası"
    )

    class Meta:
        model = Article
        fields = ["makale_adi", "makale_orjinal_path"]

    def clean_email(self):
        """E-posta adresini doğrular ve kullanıcıyı döndürür."""
        email = self.cleaned_data.get("email")

        # Kullanıcıyı bul veya oluştur
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,  
                role="yazar"  # Varsayılan rol 'yazar'
            )

        return email

    def save(self, commit=True):
        """Formdan gelen verileri işleyerek şifrelenmiş makale kaydı oluşturur."""
        instance = super().save(commit=False)

        # Kullanıcıları al
        email = self.cleaned_data.get("email")
        user = User.objects.filter(email=email).first()
        editor_email = "kayragugercin@gmail.com"
        editor_user = User.objects.filter(email=editor_email).first()

        # Eğer kullanıcılar bulunamazsa hata fırlat
        if not user:
            raise forms.ValidationError(f"Kullanıcı bulunamadı: {email}")
        if not editor_user:
            raise forms.ValidationError(f"Kullanıcı bulunamadı: {editor_email}")

        # PDF dosyasını oku
        pdf_file = self.cleaned_data.get("makale_orjinal_path")
        pdf_content = pdf_file.read()

        # 🟢 PDF şifreleme işlemi
        encrypted_pdf, encrypted_aes_key_b64, iv_b64 = encrypt_pdf_with_rsa(
            pdf_content, editor_user.get_rsa_public_key()
        )

        # Şifreli dosya adını güvenli bir şekilde oluştur
        encrypted_pdf_filename = f"{os.urandom(16).hex()}.pdf"
        encrypted_pdf_path = os.path.join(
            settings.MEDIA_ROOT, "makaleler", "orjinal", encrypted_pdf_filename
        )

        # Dosyanın varlığını kontrol et
        if os.path.exists(encrypted_pdf_path):
            raise forms.ValidationError("Şifreli dosya zaten mevcut. Lütfen tekrar deneyin.")

        # Şifrelenmiş dosyayı kaydet
        with open(encrypted_pdf_path, "wb") as f:
            f.write(encrypted_pdf)

        # 🟢 instance'a değerleri atayalım
        instance.owner = user  # Sahip kullanıcıyı atıyoruz
        instance.makale_orjinal_path.name = f"makaleler/orjinal/{encrypted_pdf_filename}"
        instance.aes_key_enc = encrypted_aes_key_b64  # Şifreli AES anahtarı
        instance.iv = iv_b64  # IV değeri

        if commit:
            instance.save()  # 🟢 Kaydetmeden önce tüm işlemler tamamlandı!

        # 🟢 FileAccess kayıtlarını oluştur
        FileAccess.objects.create_file_access(article=instance, user_owned=editor_user, user_access=editor_user)
        FileAccess.objects.create_file_access(article=instance, user_owned=editor_user, user_access=user)

        return instance
