from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .context_processors import branding
from .forms import BirthdayFlyerForm, DEFAULT_BIRTHDAY_WISH
from .models import BirthdayFlyer
from .utils import generate_birthday_flyer


def home(request):
    form = BirthdayFlyerForm()
    if request.method == 'POST':
        form = BirthdayFlyerForm(request.POST, request.FILES)
        if form.is_valid():
            flyer_record = form.save()
            brand = branding(request)['branding']
            generate_birthday_flyer(flyer_record, church_logo_path=brand['logo_path'])
            messages.success(request, 'Birthday flyer generated successfully.')
            return redirect('flyer_app:result', pk=flyer_record.pk)
    return render(
        request,
        'flyer_app/home.html',
        {
            'form': form,
            'default_wish': DEFAULT_BIRTHDAY_WISH,
        },
    )


def result(request, pk):
    flyer_record = get_object_or_404(BirthdayFlyer, pk=pk)
    return render(request, 'flyer_app/result.html', {'record': flyer_record})
