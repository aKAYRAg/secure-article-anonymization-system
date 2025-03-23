from django.shortcuts import render
from article.models import Article
from django.shortcuts import render, get_object_or_404
# Create your views here.

def editor(request):
    articles = Article.objects.all()  # Tüm makaleleri çekiyoruz
    return render(request, 'editor.html', {'articles': articles})



def makale_detay(request, makale_id):
    makale = get_object_or_404(Article, id=makale_id)  # Makaleyi getir, yoksa 404 ver
    return render(request, 'makale_detay.html', {'makale': makale})