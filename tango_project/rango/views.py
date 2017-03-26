from django.shortcuts import render


def index(request):
    context_dict = {'boldmessage': 'He at least has a life!'}
    return render(request, 'rango/index.html', context_dict)


def about(request):
    context_dict = {'name': 'JMJAC'}
    return render(request, 'rango/about.html', context_dict)

