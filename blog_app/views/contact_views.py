from django.shortcuts import render, redirect
from django.contrib import messages
from blog_app.forms import ContactUs as ContactUsForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()           
            messages.success(request, 'Your message successfully sent. Thank you!')
            return redirect('blog_app:contact_view')
        else:
            messages.error(request, 'There was an error in your form. Please check it.')
    else:
        form = ContactUsForm()

    context = {
        'form': form,
    }
    return render(request, 'blog_app/contact.html', context)