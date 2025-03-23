from django.db import models
from sifreleme.utils import generate_rsa_keys
import base64

class UserManager(models.Manager):
    def create_user(self, email, role='yazar'):
        if not email:
            raise ValueError('Email zorunludur.')

        public_key, private_key = generate_rsa_keys()

        user = self.create(
            email=email,
            role=role,
            rsa_private_key=private_key,
            rsa_public_key=public_key
        )
        return user

    def get_by_email(self, email):
        return self.filter(email=email).first()

class User(models.Model):
    ROLE_CHOICES = [
        ('yazar', 'Yazar'),
        ('editor', 'Editör'),
        ('hakem', 'Hakem'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='yazar')

    rsa_public_key = models.TextField(null=True, blank=True)
    rsa_private_key = models.TextField(null=True, blank=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.email} - {self.role}"

    def get_rsa_public_key(self):
        return self.rsa_public_key

    def get_rsa_private_key(self):
        return self.rsa_private_key

    def get_id(self):
        return self.id
