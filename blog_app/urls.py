from django.urls import path
from blog_app.views import post
from blog_app.views import user
from blog_app.views.post import add_comment
from blog_app.views.contact_views import contact_view


app_name = 'blog_app'

urlpatterns = [
    # Post related URLs
    path('', post.post_list, name='post_list'),
    path('new/', post.create_post, name='create_post'),
    path('search/', post.search_results, name='search_results'),
    path('@<str:username>/<slug:slug>/', post.post_detail, name='post_detail'),
    path('@<str:username>/<slug:slug>/like/', post.like_post, name='like_post'),
    path('@<str:username>/<slug:slug>/edit/', post.edit_post, name='edit_post'), 

    # Comment related
    path('posts/<slug:slug>/comment/add/', add_comment, name='add_comment'),

    # User account related URLs
    path('account/signup/', user.user_register, name='signup'),
    path('account/login/', user.custom_user_login, name='login'),
    path('account/logout/', user.user_logout, name='logout'),
    path('account/@<str:username>/', user.user_profile, name='user_profile'),
    path('account/@<str:username>/edit/', user.edit_profile, name='edit_profile'),

    # Other
    path('contact/', contact_view, name='contact_view'),
]
