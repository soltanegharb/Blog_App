from django.contrib import admin
from blog_app.admin import BaseAdmin
from blog_app.models import Post
from blog_app.models import Like
from blog_app.models import Comment
from taggit.models import TaggedItem
 
 
@admin.register(Post)
class PostAdmin(BaseAdmin):
   list_display = ('title', 'author', 'status', 'created_at')
   search_fields = ('title', 'content', 'author__username')
   list_filter = ('status', 'tags', 'author')


@admin.register(Like)
class LikeAdmin(BaseAdmin):
    list_display = ('user', 'post')
    search_fields = ('user__username',)
    list_filter = ('user',)
   

@admin.register(TaggedItem)
class TagAdmin(BaseAdmin):
    list_display = ('tag',)
    search_fields = ('tag',)
    list_filter = ('tag',)
    
    
@admin.register(Comment)
class CommentAdmin(BaseAdmin):
   list_display = ('post', 'user', 'content')
   search_fields = ('content',)
   list_filter = ('user', 'post')
    

 
