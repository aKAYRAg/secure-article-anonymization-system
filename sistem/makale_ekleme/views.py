from django.shortcuts import render
from django.http import HttpResponse
from .forms import ArticleForm

# Create your views here.

def makale_olustur(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            # Formu kaydet ve makale sahibi olarak e-posta adresine göre kullanıcıyı atayın
            article = form.save()
            return HttpResponse(f"Oluşturulan Makale ID: {article.id}") 

    else:
        form = ArticleForm()

    return render(request, 'makale_ekleme/makale_olustur.html', {'form': form})
