from django.shortcuts import render, HttpResponseRedirect, HttpResponse, reverse, redirect
from rango.models import Category, Page, User, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.webhose_search import run_query


# A Helper method
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookies(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookies(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


# A Helper method
def get_server_side_cookies(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def index(request):
    visitor_cookie_handler(request)
    context_dict = {'categories': Category.objects.order_by('-likes')[:5], 'pages': Page.objects.order_by('-views')[:5], 'visits': request.session['visits']}
    return render(request, 'rango/index.html', context_dict)


def about(request):
    context_dict = {'name': 'JMJAC'}
    return render(request, 'rango/about.html', context_dict)


def show_category(request, category_name_slug):
    context_dict = {'result_list': []}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    # Search functionality
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            context_dict['result_list'] = run_query(query)

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # if the form is valid commit and direct user to index
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    return render(request, 'rango/add_page.html', {'form': form, 'category': category})


# Old, not used
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


# Old, not used
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            print(f'Invalid login details {username}, {password}')
            return render(request, 'rango/login.html', {'error': 'Invalid login details'})
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


# Old, not used
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            return redirect(page.url)
        except Exception as e:
            return HttpResponse(f'Page id {page_id} not found. Error code: {e}')
    print('No page id in get string')
    return redirect(reverse('index'))


@login_required
def register_profile(request):
    form = UserProfileForm
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profie = form.save(commit=False)
            user_profie.user = request.user
            user_profie.save()
            picture = form.picture

            return redirect(reverse('index'))
        else:
            print(form.errors)

    return render(request, 'registration/profile_registration.html', {'form': form})


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect(reverse('index'))

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})

    if user.username == userprofile.user.username:
        if request.method == "POST":
            form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
            if form.is_valid():
                form.save(commit=True)
                return redirect(reverse('rango:profile', kwargs={'username': user.username}))
            else:
                print(form.errors)
    return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})


def list_profile(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html', {'userprofile_list': userprofile_list})
