from django.db import models
from django.utils.text import slugify
from blog_app.models.user import TimeStampModel, CustomUser
from taggit.managers import TaggableManager


class Post(TimeStampModel):
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('drafted', 'Drafted')
    ]
    content = models.TextField()     
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Drafted'
    )
    tags = TaggableManager(blank=True)
    
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