from django.shortcuts import render, redirect
from django.contrib import messages
from blog_app.forms import ContactUs as ContactUsForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            print(f"contact contents:\n{form.cleaned_data}")
            messages.success(request, 'Your message successfully sent. Thank you!')
            return redirect('blog_app:contact_view')
        else:
            messages.error(request, 'There\'s error in your form please check it.')
    else:
        form = ContactUsForm()

    context = {
        'form': form,
        'page_title': "contact_us"
    }
    return render(request, 'blog_app/contact.html', context)