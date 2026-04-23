from django import forms
from django.conf import settings

from .models import BirthdayFlyer

DEFAULT_BIRTHDAY_WISHES = (
    'May the Lord bless you, keep you, prosper you, and cause His face to shine '
    'upon you always. Wishing you joy, peace, divine health, and greater grace in this new year.',
    'May this new year of your life overflow with joy, divine favor, and testimonies. '
    'May God strengthen you and establish every good thing concerning you.',
    'Wishing you peace that surpasses understanding, renewed strength, and abundant grace. '
    'May your days be filled with love, laughter, and the goodness of God.',
)
DEFAULT_BIRTHDAY_WISH = DEFAULT_BIRTHDAY_WISHES[0]


def get_default_birthday_wish(seed=None):
    if seed is None:
        return DEFAULT_BIRTHDAY_WISH
    return DEFAULT_BIRTHDAY_WISHES[seed % len(DEFAULT_BIRTHDAY_WISHES)]


class BirthdayFlyerForm(forms.ModelForm):
    class Meta:
        model = BirthdayFlyer
        fields = ['celebrant_name', 'birthday_date', 'uploaded_photo', 'wish', 'theme']
        widgets = {
            'celebrant_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'birthday_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'uploaded_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'wish': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'wish': 'Leave blank to use the church default birthday prayer.',
        }

    def clean_uploaded_photo(self):
        photo = self.cleaned_data.get('uploaded_photo')
        if not photo:
            raise forms.ValidationError('Please upload a celebrant photo.')

        valid_types = {'image/jpeg', 'image/jpg', 'image/png'}
        if photo.content_type not in valid_types:
            raise forms.ValidationError('Invalid image type. Use JPG, JPEG, or PNG.')

        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if photo.size > max_size_bytes:
            raise forms.ValidationError(f'Image too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB.')
        return photo

    def clean_celebrant_name(self):
        name = self.cleaned_data.get('celebrant_name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError('Please provide a valid full name (at least 3 characters).')
        return name

    def clean_wish(self):
        wish = self.cleaned_data.get('wish', '').strip()
        if wish and len(wish) > 350:
            raise forms.ValidationError('Please keep your message within 350 characters.')
        return wish
