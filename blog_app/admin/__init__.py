__all__ = ['BaseAdmin', 'PostAdmin', 'LikeAdmin', 'TagAdmin', 'CustomUserAdmin', 'Comment'] 
from blog_app.admin.base_admin import BaseAdmin
from blog_app.admin.post import PostAdmin
from blog_app.admin.post import LikeAdmin
# from blog_app.admin.post import TagAdmin
from blog_app.admin.user import CustomUserAdmin
from blog_app.admin.post import Comment