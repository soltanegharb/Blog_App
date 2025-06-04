from django import forms
from blog_app.models.contact_us import ContactUs


class ContactUs(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'message']