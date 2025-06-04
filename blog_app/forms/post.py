from django import forms
from blog_app.models.post import Post
from blog_app.models.post import Comment



class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        label="Tags",
        required=False,
        help_text="Enter tags separated by commas. Existing tags will be used, new tags will be created."
    )
    class Meta:
        model = Post
        fields = ['title', 'content', 'status']
        widgets = {
            'content': forms.Textarea(),
            'status': forms.Select(choices=Post.STATUS_CHOICES),
        }

        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']