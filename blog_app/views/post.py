from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from blog_app.models import Post, Like
from blog_app.forms.search import SearchForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.urls import reverse
from blog_app.forms.post import PostForm, CommentForm
from django.views.decorators.csrf import csrf_exempt
from blog_app.views.utils import clean_tags


@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            user_tags = form.cleaned_data['tags_input']
            clean_tags_list = clean_tags(user_tags)
            post.tags.set(clean_tags_list)
            return redirect(
                reverse(
                    'blog_app:post_detail',
                    args=[user.username, post.slug]))
        else:
            messages.error(request, 'Invalid form!')
            return render(
                request,
                'blog_app/post/create.html',
                {'form': form, 'is_editing': False}
            )
    else:
        form = PostForm()
        return render(
            request,
            'blog_app/post/create.html',
            {'form': form, 'is_editing': False}
        )

def edit_post(request, username, slug):
    post = get_object_or_404(Post, author__username=username, slug=slug)
    user = request.user

    if not (user == post.author or user.is_staff):
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('blog_app:post_detail', username=post.author.username, slug=post.slug)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        
        if form.is_valid():
            post = form.save()
            user_tags = form.cleaned_data['tags_input']
            clean_tags_list = clean_tags(user_tags)
            post.tags.set(clean_tags_list)
            return redirect(reverse('blog_app:post_detail', args=[post.author.username, post.slug]))
        else:
            return render(
                request,
                'blog_app/post/edit.html',
                {'form': form, 'post':post, 'is_editing': True}
            )
    else:
        initial_tags = ", ".join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags_input': initial_tags})
        return render(
                request,
                'blog_app/post/edit.html',
                {'form': form, 'post':post, 'is_editing': True}
            )
        
def post_list(request):
    all_posts_list = Post.objects.filter(status='published').order_by('-created_at')
    paginator = Paginator(all_posts_list, per_page=2)

    page_number = request.GET.get('page')
    try:
        posts_page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        posts_page_obj = paginator.page(1)
    except EmptyPage:
        posts_page_obj = paginator.page(paginator.num_pages)

    context = {'posts': posts_page_obj, 'page_obj': posts_page_obj}
    
    return render(request, 'blog_app/post/list.html', context)


@csrf_exempt
@login_required
def like_post(request, username, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    user = request.user
    like_instance, created = Like.objects.get_or_create(post=post, user=user)

    if not created:
        like_instance.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})


def post_detail(request, username, slug):
    post = get_object_or_404(Post, author__username=username, slug=slug)

    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view this post.")
        login_url = reverse('blog_app:login')
        return redirect(f'{login_url}?next={request.path}')

    if post.status == 'drafted' and not (request.user == post.author or request.user.is_staff):
        messages.error(request, "You do not have permission to view this draft.")
        return redirect('blog_app:user_profile', username=request.user.username)
    
    comments = post.comments.all().order_by('created_at')
    comment_form = CommentForm()
    recently_viewed_posts_slugs = request.session.get('recently_viewed', [])
    
    if post.slug not in recently_viewed_posts_slugs:
        recently_viewed_posts_slugs.insert(0, post.slug)
        request.session['recently_viewed'] = recently_viewed_posts_slugs[:5] 

    recent_posts_objects = Post.objects.filter(
        slug__in=request.session.get('recently_viewed', []), 
        status='published'
    ).order_by('-created_at') 

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'recently_viewed_posts': recent_posts_objects,
        'username': username
    }
    return render(
        request,
        'blog_app/post/detail.html',
        context=context
    )


def search_results(request):
    search_form = SearchForm(request.GET)
    query = request.GET.get('q')
    posts = Post.objects.none()

    if query:
        posts = Post.objects.filter(
        (Q(title__contains=query) | Q(content__contains=query)) & Q(status="published"))
        
        if not posts.exists():
            messages.info(request, f"No posts found for '{query}'.")

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        'search_form': search_form,
        'query': query,
        'page_obj': page_obj,
        'posts':posts,
        'username': request.user.username
    }
    return render(request, 'blog_app/post/search_results.html', context)


@login_required
@permission_required('blog_app.create_comment', raise_exception=True)
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment was added successfully.')
            return redirect('blog_app:post_detail', username=post.author.username ,slug=post.slug)
        else:
            error_summary = []
            for field, errors in form.errors.items():
                label = field.capitalize() if field != '__all__' else 'Form'
                error_summary.append(f"{label}: {', '.join(errors)}")
            messages.error(request, f"Error! Please retry: {'; '.join(error_summary)}")
    else:
        form = CommentForm()

    return redirect('blog_app:post_detail', username=post.author.username, slug=post.slug)


