from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from cryptography.hazmat.primitives import padding as symmetric_padding


def generate_rsa_keys():

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    return public_key_pem, private_key_pem


def encrypt_pdf_with_rsa(pdf_file, rsa_public_key):
    aes_key = os.urandom(32)  # 256-bit AES anahtarı
    iv = os.urandom(16)       # 128-bit IV

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Eğer pdf_file bir bytes objesi ise, zaten okunmuş olur
    if isinstance(pdf_file, bytes):
        pdf_data = pdf_file
    else:
        pdf_data = pdf_file.read()  # Dosya nesnesi ise .read() ile içeriği al

    # AES CBC için PKCS7 padding eklenmesi
    padder = symmetric_padding.PKCS7(128).padder()
    padded_data = padder.update(pdf_data) + padder.finalize()

    encrypted_pdf_data = encryptor.update(padded_data) + encryptor.finalize()

    # RSA public key'i yükle
    public_key = serialization.load_pem_public_key(
        rsa_public_key.encode(),
        backend=default_backend()
    )

    # AES anahtarını RSA ile şifrele
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Şifreli PDF'yi bytes olarak döndür
    return encrypted_pdf_data, base64.b64encode(encrypted_aes_key).decode('utf-8'), base64.b64encode(iv).decode('utf-8')







def encrypt_aes_key_with_rsa(aes_key, rsa_public_key):

    public_key = serialization.load_pem_public_key(
        rsa_public_key.encode(),
        backend=default_backend()
    )

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(encrypted_aes_key).decode('utf-8')




def decrypt_aes_key_with_private_key(encrypted_aes_key, rsa_private_key):

    private_key = serialization.load_pem_private_key(
        rsa_private_key.encode(),
        password=None,
        backend=default_backend()
    )

    aes_key = private_key.decrypt(
        base64.b64decode(encrypted_aes_key),
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return aes_key


def decrypt_pdf_with_aes(encrypted_pdf_data, aes_key, iv):

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # PDF verisini çözme
    decrypted_padded_data = decryptor.update(encrypted_pdf_data) + decryptor.finalize()

    # PKCS7 padding'i kaldırma
    unpadder = symmetric_padding.PKCS7(128).unpadder()
    decrypted_pdf_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return decrypted_pdf_data


def decrypt_pdf_with_rsa_and_aes(encrypted_pdf_data, encrypted_aes_key, iv, rsa_private_key):

    # RSA özel anahtarı ile AES anahtarını çöz
    aes_key = decrypt_aes_key_with_private_key(encrypted_aes_key, rsa_private_key)

    # AES ile PDF verisini çöz
    decrypted_pdf_data = decrypt_pdf_with_aes(encrypted_pdf_data, aes_key, base64.b64decode(iv))

    return decrypted_pdf_data