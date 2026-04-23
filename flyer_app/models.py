from django.db import models


def upload_photo_path(instance, filename):
    return f'uploads/{filename}'


def generated_flyer_path(instance, filename):
    return f'generated_flyers/{filename}'


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
