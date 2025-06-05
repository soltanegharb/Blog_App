from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth import logout, authenticate, login
from blog_app.models import CustomUser, Post
from blog_app.forms.user import CustomLoginForm
from blog_app.forms import UserProfile
from django.contrib import messages
from blog_app.forms.user import UserRegistration
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def user_register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('blog_app:post_list')

    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            pw = form.cleaned_data['password']
            pw_confirm = form.cleaned_data['password_confirm']

            if pw != pw_confirm:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'registration/signup.html', {'form': form})


            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Registration successful, {user.username}! You are now logged in.')
            return redirect('blog_app:post_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistration()

    return render(request, 'registration/signup.html', {'form': form})


def custom_user_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('blog_app:post_list')

    message_to_display = None
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)            
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect(next_url or resolve_url(settings.LOGIN_REDIRECT_URL))
            else:
                message_to_display = 'Invalid username or password.'
                messages.error(request, message_to_display)
        else:
            message_to_display = 'Form data is invalid. Please check your input.'
            messages.error(request, message_to_display)
    else:
        form = CustomLoginForm()
    
    context = {'form': form } 
    return render(request, 'blog_app/user/custom_login.html', context=context) 


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been successfully logged out.")
    else:
        messages.info(request, "You are not currently logged in.")
    return redirect('blog_app:post_list')


def user_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    
    user_posts_qs = Post.detailed.user_posts_with_details(user=profile_user)

    paginator = Paginator(user_posts_qs, per_page=5)
    page_number = request.GET.get('page')
    try:
        user_posts_page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        user_posts_page_obj = paginator.page(1)
    except EmptyPage:
        user_posts_page_obj = paginator.page(paginator.num_pages)

    context = {
        'profile_user': profile_user,
        'user_posts': user_posts_page_obj,
    }
    return render(request, 'blog_app/user/user_profile.html', context)


@login_required
def edit_profile(request, username):
    user_to_edit = get_object_or_404(CustomUser, username=username)

    if not (request.user == user_to_edit or request.user.is_staff):
        messages.error(request, "Sorry! You don't have permission for this.")
        return redirect('blog_app:user_profile', username=request.user.username if request.user.is_authenticated else user_to_edit.username)

    if request.method == 'POST':
        form = UserProfile(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            updated_user = form.save()
            messages.success(request, 'Your profile updated successfully!')
            return redirect('blog_app:user_profile', username=updated_user.username) 
        else:
            error_list = [f"{field.label if field.label else field.name.capitalize()}: {', '.join(errors)}" for field, errors in form.errors.items()]
            messages.error(request, f"Please fix errors: {'; '.join(error_list)}")
    else:
        form = UserProfile(instance=user_to_edit)

    context = {
        'form': form,
        'profile_user': user_to_edit
    }
    return render(request, 'blog_app/user/user_profile_form.html', context)