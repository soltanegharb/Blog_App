from django.db import models
from django.db.models.query import QuerySet
from django.utils.text import slugify
from blog_app.models.user import TimeStampModel, CustomUser
from taggit.managers import TaggableManager


class PostQuerySet(models.QuerySet):
    def with_details(self):
        return self.select_related('author').prefetch_related('tags', 'likes', 'comments__user')


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def published_posts_with_details(self):
        return self.get_queryset() \
                   .filter(status=Post.STATUS_PUBLISHED) \
                   .with_details() \
                   .order_by('-created_at')

    def user_posts_with_details(self, user):
        return self.get_queryset() \
                   .filter(author=user) \
                   .with_details() \
                   .order_by('-created_at')
    
    def get_post_by_slug_with_details(self, slug, author_username=None, status=None):
        qs = self.get_queryset().with_details()
        query_params = {'slug': slug}
        if author_username:
            query_params['author__username'] = author_username
        if status:
            query_params['status'] = status
        return qs.get(**query_params)


class Post(TimeStampModel):
    STATUS_DRAFTED = 'drafted'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFTED, 'Drafted'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    content = models.TextField()     
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFTED
    )
    tags = TaggableManager(blank=True)
    
    objects = models.Manager()
    detailed = PostManager()

    def __str__(self):
        return f'{self.title}'
    
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            qs = Post.objects.filter(slug=self.slug) 
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                qs = Post.objects.filter(slug=self.slug)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)

        super().save(*args, **kwargs)


class Comment(TimeStampModel):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    
    class Meta:
        permissions = [('create_comment', 'Can create comment.')]

class Like(TimeStampModel):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'Like by {self.user.username} on {self.post.title}'