from django.shortcuts import render
from rango.models import Category, Page


def index(request):
    context_dict = {'categories': Category.objects.order_by('-likes')[:5], 'pages': Page.objects.order_by('-views')[:5]}
    return render(request, 'rango/index.html', context_dict)


def about(request):
    context_dict = {'name': 'JMJAC'}
    return render(request, 'rango/about.html', context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context_dict)
