import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_project.settings')
django.setup()

from rango.models import Category, Page


def populate():
    # Populates database with data
    python_pages = [{"title": "Official Python Tutorial", "url": "http://docs.python.org/2/tutorial/"},
                    {"title": "How to Think like a Computer Scientist", "url": "http://www.greenteapress.com/thinkpython/"},
                    {"title": "Learn Python in 10 Minutes","url": "http://www.korokithakis.net/t utorials/python/"}]

    django_pages = [
        {"title": "Official Django Tutorial",
         "url": "https://docs.djangoproject.com/en/1.9/intro/tutorial01/", "views": 32},
        {"title": "Django Rocks",
         "url": "http://www.djangorocks.com/", "views": 16},
        {"title": "How to Tango with Django",
         "url": "http://www.tangowithdjango.com/", "views": 8}]

    other_pages = [
        {"title": "Bottle", "url": "http://bottlepy.org/docs/dev/", "views": 32},
        {"title": "Flask", "url": "http://flask.pocoo.org", "views": 16}]

    cats = {"Python": {"pages": python_pages},
            "Django": {"pages": django_pages},
            "Other Frameworks": {"pages": other_pages}}
    for cat, cat_data in cats.items():
        for page in cat_data["pages"]:
            add_page(add_cat(cat), page["title"], page["url"])

    for c in Category.objects.all():
        for p in Page.objects.all():
            print(f'- {p} - {c}')


def add_page(cat, title, url, views = 0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()
