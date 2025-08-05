from django.shortcuts import render, redirect
from .models import Post, Comment, Tag, Profile, WebsiteMetadata
from .forms import CommentForm, SubscriberForm, RegistrationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth import login


# Create your views here.
def index(request):
    posts = Post.objects.all()
    top_posts = posts.order_by('-view_count')[:3]
    recent_posts = posts.order_by('-updated_at')[:3]
    featured_blogs = posts.filter(is_featured=True)
    subscriber_form = SubscriberForm()
    subscribe_msg = None
    website_metadata = None
    
    if WebsiteMetadata.objects.exists():
        website_metadata = WebsiteMetadata.objects.first()
    
    if featured_blogs:
        featured_blogs = featured_blogs[0]  # Get the first featured blog
    
    if request.method == 'POST':
        subscriber_form = SubscriberForm(request.POST)
        if subscriber_form.is_valid():
            subscriber_form.save()
            request.session['subscribed'] = True
            subscribe_msg = 'Thank you for subscribing!'
            subscriber_form = SubscriberForm()
            
            # return redirect('index')
    
    context = {
            'posts': posts, 
            'top_posts': top_posts, 
            'recent_posts': recent_posts, 
            'subscriber_form': subscriber_form, 
            'subscribe_msg': subscribe_msg, 
            'featured_blogs': featured_blogs,
            'website_metadata': website_metadata,
        }
    return render(request, 'blogapp/index.html', context)


def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post, parent=None)
    form = CommentForm()
    
    # Bookmark logic
    bookmarked = False
    if post.bookmarks.filter(id=request.user.id).exists():
        bookmarked = True
    is_bookmarked = bookmarked
    
    # likes logic
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    post_is_liked = liked
    num_of_likes = post.num_of_likes()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            if request.POST.get('parent'):
                parent = request.POST.get('parent')
                parent_obj = Comment.objects.get(id=parent)
                if parent_obj:
                    comment_reply = comment_form.save(commit=False)
                    comment_reply.parent = parent_obj
                    comment_reply.post = post
                    comment_reply.save()
                    return redirect('post_page', slug=post.slug)
            else:    
                comment = comment_form.save(commit=False)
                post_id = request.POST.get('post_id')
                post = Post.objects.get(id = post_id)
                comment.post = post
                comment.save()
                return redirect('post_page', slug=post.slug)
        
    if post.view_count is None:
        post.view_count = 1
    else:
        post.view_count += 1
    post.save()
    
    #sidebar data
    recent_posts = Post.objects.exclude(id = post.id).order_by('-updated_at')[:3]
    top_authors = User.objects.annotate(number=Count('post')).order_by('-number')[:3]
    tags = Tag.objects.all()
    related_posts = Post.objects.exclude(id = post.id).filter(author = post.author)[:3]
    
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'is_bookmarked': is_bookmarked,
        'post_is_liked': post_is_liked,
        'num_of_likes': num_of_likes,
        'recent_posts': recent_posts,
        'top_authors': top_authors,
        'tags': tags,
        'related_posts': related_posts,
    }
    return render(request, 'blogapp/post_page.html', context)


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    all_tags = Tag.objects.all()
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[:3]
    recent_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-updated_at')[:3]
    context = {
        'tag': tag,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'all_tags': all_tags,
        }
    return render(request, 'blogapp/tag_page.html', context)


def author_page(request, slug):
    profile = Profile.objects.get(slug=slug)
    top_posts = Post.objects.filter(author = profile.user).order_by('-view_count')[:3]
    recent_posts = Post.objects.filter(author = profile.user).order_by('-updated_at')[:3]
    top_authors = User.objects.annotate(number = Count('post')).order_by('-number')[:3]
    
    context = {
        'profile': profile,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'top_authors': top_authors,
        }
    return render(request, 'blogapp/author_page.html', context)
    
    
def search_page(request):
    search_query = request.GET.get('q')
    if search_query:
        posts = Post.objects.filter(title__icontains=search_query)
    else:
        posts = Post.objects.none()  # Return an empty queryset if no query is provided
    
    top_posts = posts.order_by('-view_count')[:3]
    recent_posts = posts.order_by('-updated_at')[:3]
    
    context = {
        'posts': posts,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'search_query': search_query
    }
    return render(request, 'blogapp/search_page.html', context)


def about_page(request):
    website_metadata = None
    if WebsiteMetadata.objects.exists():
        website_metadata = WebsiteMetadata.objects.first()
    
    context = {
        'website_metadata': website_metadata
    }
    return render(request, 'blogapp/about_page.html', context)


def registration_page(request):
    registration_form = RegistrationForm()
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            user = registration_form.save()
            login(request, user)
            return redirect('index')
    context = {
        'registration_form': registration_form
    }
    return render(request, 'registration/registration.html', context)
    

@login_required 
def bookmarked_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        if post.bookmarks.filter(id=request.user.id).exists():
            post.bookmarks.remove(request.user)
        else:
            post.bookmarks.add(request.user)
        return redirect('post_page', slug=slug)  # Redirect to the post page
    return redirect('post_page', slug=slug)  # Always return a response


@login_required 
def liked_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('post_page', slug=slug)  # Redirect to the post page
    return redirect('post_page', slug=slug)  # Always return a response


def all_bookmarked_posts(request):
    all_bookmarked_posts = Post.objects.filter(bookmarks=request.user)
    context = {'all_bookmarked_posts': all_bookmarked_posts}
    return render(request, 'blogapp/all_bookmarked_posts.html', context)
    
def all_posts(request):
    all_posts = Post.objects.all()
    context = {'all_posts': all_posts}
    return render(request, 'blogapp/all_posts.html', context)

def all_liked_posts(request):
    all_liked_posts = Post.objects.filter(likes=request.user)
    context = {'all_liked_posts': all_liked_posts}
    return render(request, 'blogapp/all_liked_posts.html', context)