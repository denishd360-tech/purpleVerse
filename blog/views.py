
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.utils.text import slugify

import requests

from .models import Post, Category, Comment, PostLike, Bookmark
from .forms import PostForm


def home(request):
    posts = Post.objects.filter(
        status='published'
    ).select_related(
        'author', 'category'
    ).order_by('-created_at')

    categories = Category.objects.all()
    query = request.GET.get('q', '').strip()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    return render(request, 'blog/home.html', {
        'posts': posts,
        'categories': categories,
        'query': query,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        Post, slug=slug, status='published'
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        body = request.POST.get('body', '').strip()

        if name and body:
            Comment.objects.create(
                post=post,
                name=name,
                body=body
            )
            messages.success(
                request, 'Comment added successfully!'
            )
            return redirect('post_detail', slug=post.slug)

        messages.error(
            request, 'Please enter your name and comment.'
        )

    comments = post.comments.order_by('-created_at')
    liked = False
    bookmarked = False

    if request.user.is_authenticated:
        liked = PostLike.objects.filter(
            post=post, user=request.user
        ).exists()

        bookmarked = Bookmark.objects.filter(
            post=post, user=request.user
        ).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'liked': liked,
        'bookmarked': bookmarked,
    })


@login_required
@require_POST
def toggle_like(request, slug):
    post = get_object_or_404(
        Post, slug=slug, status='published'
    )

    like, created = PostLike.objects.get_or_create(
        post=post, user=request.user
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    likes_count = PostLike.objects.filter(
        post=post
    ).count()

    return JsonResponse({
        'likes': likes_count,
        'liked': liked,
    })

@login_required
def create_post(request):
    print("CREATE_POST CALLED:", request.method)

    if request.method == 'POST':
        print("CREATE_POST CALLED:", request.method)
        form = PostForm(request.POST, request.FILES)
        print("POST DATA:", request.POST)
        print("FORM VALID:", form.is_valid())
        print("FORM ERRORS:", form.errors)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', slug=post.slug)
        print("CREATE_POST CALLED:", request.method)

        print("FORM ERRORS:", form.errors)
        messages.error(request, f"Post save failed: {form.errors}")

    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Create Post',
    })





@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:
        messages.error(request, 'You cannot edit this post.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(
            request.POST, request.FILES, instance=post
        )

        if form.is_valid():
            form.save()
            messages.success(
                request, 'Post updated successfully!'
            )
            return redirect('post_detail', slug=post.slug)

        messages.error(
            request,
            'Post update ആയില്ല. ഫീൽഡുകളിലെ പിശകുകൾ പരിശോധിക്കുക.'
        )

    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Edit Post',
    })


@login_required
@require_POST
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:
        messages.error(
            request, 'You cannot delete this post.'
        )
        return redirect('home')

    post.delete()
    messages.success(
        request, 'Post deleted successfully!'
    )
    return redirect('home')


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)

    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related(
        'author', 'category'
    ).order_by('-created_at')

    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts': posts,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 'Account created successfully!'
            )
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form,
    })


@login_required
def profile(request):
    posts = Post.objects.filter(
        author=request.user
    ).order_by('-created_at')

    bookmarks = Bookmark.objects.filter(
        user=request.user
    ).select_related('post')

    return render(request, 'blog/profile.html', {
        'profile_user': request.user,
        'posts': posts,
        'bookmarks': bookmarks,
    })


@login_required
@require_POST
def toggle_bookmark(request, slug):
    post = get_object_or_404(
        Post, slug=slug, status='published'
    )

    bookmark, created = Bookmark.objects.get_or_create(
        post=post, user=request.user
    )

    if not created:
        bookmark.delete()
        saved = False
    else:
        saved = True

    return JsonResponse({'saved': saved})


@login_required
@require_POST
def ai_write_post(request):
    topic = request.POST.get('topic', '').strip()

    if not topic:
        messages.error(
            request, 'Please enter a blog topic.'
        )
        return redirect('create_post')

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5:3b',
                'prompt': (
                    'Write a professional blog post in English '
                    f'about: {topic}\n'
                    'The first line must be exactly in this format: '
                    'Title: A suitable blog title\n'
                    'After the first line, write the full blog content. '
                    'Do not repeat the title in the content.'
                ),
                'stream': False,
            },
            timeout=180,
        )
        response.raise_for_status()

        generated = response.json().get(
            'response', ''
        ).strip()

        if not generated:
            messages.error(
                request, 'AI did not generate content.'
            )
            return redirect('create_post')

        lines = generated.splitlines()
        title = topic.title()
        content = generated

        if lines:
            first_line = lines[0].strip()

            if first_line.lower().startswith('title:'):
                title = first_line.split(':', 1)[1].strip()
                content = '\n'.join(lines[1:]).strip()

        if not title:
            title = topic.title()

        if not content:
            content = generated

        base_slug = slugify(title)[:50].strip('-') or 'ai-blog'
        unique_slug = base_slug
        counter = 2

        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{base_slug}-{counter}'
            counter += 1

        form = PostForm(initial={
            'title': title,
            'slug': unique_slug,
            'content': content,
            'status': 'published',
        })

        messages.success(
            request,
            'AI content തയ്യാറായി. പരിശോധിച്ച് Save Post അമർത്തുക.'
        )

        return render(request, 'blog/post_form.html', {
            'form': form,
            'title': 'Create Post',
            'ai_topic': topic,
        })

    except requests.RequestException:
        messages.error(
            request,
            'Ollama-യുമായി ബന്ധപ്പെടാൻ കഴിഞ്ഞില്ല. Ollama പ്രവർത്തിക്കുന്നുണ്ടോ എന്ന് പരിശോധിക്കുക.'
        )
        return redirect('create_post')

