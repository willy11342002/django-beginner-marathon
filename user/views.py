from django.shortcuts import redirect
from django.shortcuts import render
from .forms import UserCreationForm


def index(request):
    return render(request, 'index.html')


def signup(request):
    data = request.POST or None
    form = UserCreationForm(data)

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})
