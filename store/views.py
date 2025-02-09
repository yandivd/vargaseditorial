from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Book, Category
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):

    books = Book.objects.filter(existencia=True)
    best_selling_books = Book.objects.all().order_by('-sales_amount')[:5]
    best_rated = Book.objects.all().order_by('-valoration')[:3]
    added_latest = Book.objects.all().order_by('-date_added')[:3]
    recomendated_books = Book.objects.filter(recomendated=True)[:3]
    discount_books = Book.objects.filter(discount__isnull=False).order_by('-discount')[:3]
    categories = Category.objects.all()

    return render(request, 'index.html', {
        'books':books,
        'best_rated': best_rated,
        'best_selling_books': best_selling_books,
        'added_latest': added_latest,
        'recomendated_books':recomendated_books,
        'discount_books': discount_books,
        'categories': categories
    })


def tienda(request):

    books = Book.objects.filter(existencia=True)
    best_selling_books = Book.objects.all().order_by('-sales_amount')[:5]
    best_rated = Book.objects.all().order_by('-valoration')[:3]
    added_latest = Book.objects.all().order_by('-date_added')[:3]
    recomendated_books = Book.objects.filter(recomendated=True)[:3]
    discount_books = Book.objects.filter(discount__isnull=False).order_by('-discount')[:3]
    categories = Category.objects.all()

    for i in books:
        print(i)
    return render(request, 'tienda.html', {
        'books':books,
        'best_rated': best_rated,
        'best_selling_books': best_selling_books,
        'added_latest': added_latest,
        'recomendated_books':recomendated_books,
        'discount_books': discount_books,
        'categories': categories
    })

def api_books(request):
    books = Book.objects.filter(existencia = True)
    book_list = []

    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "price": book.price,
            "discount": book.discount,
            "discounted_price": book.discounted_price(),
            "rating": book.valoration,
            "img": {
                "url": book.img.url
            }
        }
        book_list.append(book_data)

    return JsonResponse(book_list, safe=False)

def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    print(book.valoration)
    return render(request, 'book_detail.html', {'book': book})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/crm/'})  # Cambia la URL de redirección según sea necesario
        else:
            return JsonResponse({'success': False, 'message': 'Credenciales inválidas'}, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('index')  # Cambia 'login' por la vista a la que quieras redirigir

def get_book_price(request, id):
    try:
        book = Book.objects.get(id=id)
        
        if book.discount is not None and book.discount > 0:
            precio_libro = round(book.price * (1 - (book.discount / 100)))
        else:
            precio_libro = book.price
        
        return JsonResponse({
            'precio': precio_libro,
        })
    
    except Book.DoesNotExist:
        return JsonResponse({
            'error': "El libro no existe.",
        }, status=404)

