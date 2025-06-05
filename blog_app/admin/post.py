from django.contrib import admin, messages
from django.urls import path, reverse, NoReverseMatch
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect
from django.middleware.csrf import get_token

from blog_app.admin.base_admin import BaseAdmin
from blog_app.models import Post, Like, Comment
from taggit.models import TaggedItem


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ('user', 'content', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 1
    ordering = ('-created_at',)
    fk_name = 'post'
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at', 'word_count', 'like_count', 'comment_count', 'current_admin_like_status')
    list_filter = ('status', 'author__username', 'created_at', 'tags')
    search_fields = ('title', 'content', 'author__username', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    list_select_related = ('author',)

    readonly_fields_base = ['created_at', 'updated_at', 'like_count', 'comment_count', 'word_count'] 

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Status and Categorization', {
            'fields': ('status', 'tags')
        }),
        ('Timestamps and Stats', {
            'fields': (
                'created_at', 
                'updated_at', 
                'like_count',
                'comment_count',
                'word_count',
                'admin_like_button'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CommentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related('tags', 'likes', 'comments')

    def word_count(self, obj):
        return len(obj.content.split()) if obj.content else 0
    word_count.short_description = 'Word Count'

    def like_count(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'likes' in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache['likes'])
        if obj.pk: 
            return obj.likes.count()
        return 0
    like_count.short_description = 'Likes'
    like_count.admin_order_field = 'likes__count'

    def comment_count(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'comments' in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache['comments'])
        if obj.pk: 
            return obj.comments.count()
        return 0
    comment_count.short_description = 'Comments'
    comment_count.admin_order_field = 'comments__count'

    def current_admin_like_status(self, obj):
        request_user = getattr(self, 'request_user', getattr(self, 'current_user', None))
        if obj.pk and request_user and request_user.is_authenticated:
            if Like.objects.filter(post=obj, user=request_user).exists():
                return "Liked by You"
            return "Not Liked by You"
        return "N/A (Save post first)"
    current_admin_like_status.short_description = 'Your Like Status'

    def admin_like_button(self, obj):
        if not obj.pk:
            return format_html('<button type="button" class="button" disabled>Like this Post</button>   (Save post to enable liking)')

        admin_user = getattr(self, 'request_user', None)
        csrf_token = getattr(self, 'csrf_token_value', '')

        if not admin_user or not admin_user.is_authenticated:
             return "User context unavailable"
        if not csrf_token:
            return "CSRF token unavailable"

        is_liked_by_admin = Like.objects.filter(post=obj, user=admin_user).exists()
        button_text = "Unlike this Post" if is_liked_by_admin else "Like this Post"
        
        admin_site_name = self.admin_site.name
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        url_name_component = f'{app_label}_{model_name}_toggle_like'
        fully_qualified_view_name = f'{admin_site_name}:{url_name_component}'
        
        try:
            action_url = reverse(fully_qualified_view_name, args=[obj.pk])
        except NoReverseMatch as e:
            return format_html("<strong style='color:red;'>Error reversing URL '{}': {}</strong>", fully_qualified_view_name, str(e))

        button_id = f"toggle-like-button-{obj.pk}"
        html_button = format_html(
            '<button type="button" id="{}" data-action-url="{}" data-csrf-token="{}" class="button">{}</button>',
            button_id, action_url, csrf_token, button_text
        )
        js_script = format_html(
            '''<script>
            (function() {{
                var button = document.getElementById("{button_id}");
                if (button && !button.disabled && !button.getAttribute('listener-attached')) {{
                    button.setAttribute('listener-attached', 'true');
                    button.addEventListener('click', function(e) {{
                        e.preventDefault();
                        var form = document.createElement('form');
                        form.method = 'POST';
                        form.action = this.getAttribute('data-action-url');
                        var csrfInput = document.createElement('input');
                        csrfInput.type = 'hidden';
                        csrfInput.name = 'csrfmiddlewaretoken';
                        csrfInput.value = this.getAttribute('data-csrf-token');
                        form.appendChild(csrfInput);
                        document.body.appendChild(form);
                        form.submit();
                        document.body.removeChild(form);
                    }});
                }}
            }})();
            </script>''',
            button_id=button_id
        )
        return html_button + js_script
    admin_like_button.short_description = 'Admin Like/Unlike'

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta
        url_pattern_name = f'{opts.app_label}_{opts.model_name}_toggle_like'
        custom_urls = [
            path(
                '<path:object_id>/toggle-like/',
                self.admin_site.admin_view(self.process_toggle_like),
                name=url_pattern_name 
            ),
        ]
        return custom_urls + urls

    def process_toggle_like(self, request, object_id):
        if request.method != 'POST':
            messages.error(request, "This action requires a POST request.")
            change_url_name = f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change'
            redirect_fallback_url = reverse(change_url_name, args=[object_id])
            referer_url = request.META.get('HTTP_REFERER', redirect_fallback_url)
            return redirect(referer_url)

        post = get_object_or_404(Post, pk=object_id)
        admin_user = request.user
        
        try:
            like_instance, created = Like.objects.get_or_create(post=post, user=admin_user)
            if not created:
                like_instance.delete()
                messages.success(request, f"You (admin) have UNLIKED the post: '{post.title}'.")
            else:
                messages.success(request, f"You (admin) have LIKED the post: '{post.title}'.")
        except Exception as e:
            messages.error(request, f"An error occurred during like/unlike: {e}")
        
        change_url_name = f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change'
        redirect_url = reverse(change_url_name, args=[post.pk])
        return redirect(redirect_url)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        self.request_user = request.user
        self.csrf_token_value = get_token(request)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_readonly_fields(self, request, obj=None):
        self.request_user = request.user
        ro_fields = list(self.readonly_fields_base) 
        if 'admin_like_button' not in ro_fields:
            ro_fields.append('admin_like_button')
        return tuple(ro_fields)

    def changelist_view(self, request, extra_context=None):
        self.current_user = request.user
        self.request_user = request.user
        return super().changelist_view(request, extra_context)
            
    actions = ['publish_posts', 'archive_posts', 'draft_posts', 'admin_like_posts_bulk', 'admin_unlike_posts_bulk']

    def publish_posts(self, request, queryset):
        updated_count = queryset.update(status=Post.STATUS_PUBLISHED)
        self.message_user(request, f"{updated_count} post(s) have been published.", messages.SUCCESS)
    publish_posts.short_description = "Mark selected posts as Published"

    def archive_posts(self, request, queryset):
        updated_count = queryset.update(status=Post.STATUS_ARCHIVED)
        self.message_user(request, f"{updated_count} post(s) have been archived.", messages.SUCCESS)
    archive_posts.short_description = "Mark selected posts as Archived"

    def draft_posts(self, request, queryset):
        updated_count = queryset.update(status=Post.STATUS_DRAFTED)
        self.message_user(request, f"{updated_count} post(s) have been drafted.", messages.SUCCESS)
    draft_posts.short_description = "Mark selected posts as Drafted"

    def admin_like_posts_bulk(self, request, queryset):
        admin_user = request.user
        liked_count = 0; already_liked_count = 0
        for post_obj in queryset:
            _, created = Like.objects.get_or_create(post=post_obj, user=admin_user)
            if created: liked_count += 1
            else: already_liked_count +=1
        msg_parts = []
        if liked_count: msg_parts.append(f"{liked_count} post(s) liked.")
        if already_liked_count: msg_parts.append(f"{already_liked_count} post(s) already liked by you.")
        if not msg_parts: msg_parts.append("No new likes were applied or no posts selected.")
        self.message_user(request, " ".join(msg_parts), messages.SUCCESS if liked_count > 0 else messages.INFO)
    admin_like_posts_bulk.short_description = "Like selected (as admin)"

    def admin_unlike_posts_bulk(self, request, queryset):
        admin_user = request.user
        unliked_count = 0; not_liked_count = 0
        for post_obj in queryset:
            deleted_count, _ = Like.objects.filter(post=post_obj, user=admin_user).delete()
            if deleted_count > 0: unliked_count +=1
            else: not_liked_count += 1
        msg_parts = []
        if unliked_count: msg_parts.append(f"{unliked_count} post(s) unliked.")
        if not_liked_count: msg_parts.append(f"{not_liked_count} post(s) were not liked by you.")
        if not msg_parts: msg_parts.append("No unlikes were applied or no posts selected.")
        self.message_user(request, " ".join(msg_parts), messages.SUCCESS if unliked_count > 0 else messages.INFO)
    admin_unlike_posts_bulk.short_description = "Unlike selected (as admin)"


@admin.register(Like)
class LikeAdmin(BaseAdmin):
    list_display = ('user', 'post_title', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('user__username', 'created_at', 'post__author__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['post', 'user']
    list_select_related = ('user', 'post')

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post Title'
    post_title.admin_order_field = 'post__title'


@admin.register(TaggedItem)
class TagAdmin(BaseAdmin):
    list_display = ('tag', 'content_object', 'object_id')
    search_fields = ('tag__name',)
    list_filter = ('tag',)
    autocomplete_fields = ['tag']
    list_select_related = ('tag',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
   list_display = ('post_title', 'user_username', 'short_content', 'created_at', 'updated_at')
   search_fields = ('content', 'user__username', 'post__title')
   list_filter = ('user__username', 'post__author__username', 'created_at', 'post__status')
   readonly_fields = ('created_at', 'updated_at')
   date_hierarchy = 'created_at'
   autocomplete_fields = ['post', 'user']
   list_select_related = ('user', 'post', 'post__author')

   fieldsets = (
       (None, {
           'fields': ('post', 'user', 'content')
       }),
       ('Timestamps', {
           'fields': ('created_at', 'updated_at'),
           'classes': ('collapse',)
       }),
   )

   def post_title(self, obj):
       return obj.post.title
   post_title.short_description = 'Post'
   post_title.admin_order_field = 'post__title'

   def user_username(self, obj):
       return obj.user.username
   user_username.short_description = 'User'
   user_username.admin_order_field = 'user__username'
   
   def short_content(self, obj):
       return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
   short_content.short_description = 'Content Snippet'