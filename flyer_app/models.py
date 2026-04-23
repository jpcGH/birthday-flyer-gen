from django.db import models


def upload_photo_path(instance, filename):
    return f'uploads/{filename}'


def generated_flyer_path(instance, filename):
    return f'generated_flyers/{filename}'


def branding_logo_path(instance, filename):
    return f'branding/{filename}'


class BirthdayFlyer(models.Model):
    THEME_CHOICES = [
        ('royal_gold', 'Royal Gold'),
        ('purple_grace', 'Purple Grace'),
        ('burgundy_joy', 'Burgundy Joy'),
    ]

    celebrant_name = models.CharField(max_length=120)
    birthday_date = models.DateField()
    wish = models.TextField(blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='royal_gold')
    uploaded_photo = models.ImageField(upload_to=upload_photo_path)
    generated_flyer = models.ImageField(upload_to=generated_flyer_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.celebrant_name} - {self.birthday_date}'


class SiteBranding(models.Model):
    site_title = models.CharField(max_length=150, default='RCCG City of Refuge Birthday Flyer Generator')
    navbar_title = models.CharField(max_length=150, default='RCCG City of Refuge Birthday Flyer Generator')
    footer_owner = models.CharField(max_length=150, default='RCCG City of Refuge Media Unit')
    footer_rights_text = models.CharField(max_length=120, default='All rights reserved.')
    logo = models.ImageField(upload_to=branding_logo_path, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site branding'
        verbose_name_plural = 'Site branding'
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return self.navbar_title

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).order_by('-updated_at').first() or cls.objects.order_by('-updated_at').first()

    @classmethod
    def defaults(cls):
        return {
            'site_title': 'RCCG City of Refuge Birthday Flyer Generator',
            'navbar_title': 'RCCG City of Refuge Birthday Flyer Generator',
            'footer_owner': 'RCCG City of Refuge Media Unit',
            'footer_rights_text': 'All rights reserved.',
            'logo_url': None,
            'logo_path': None,
        }
