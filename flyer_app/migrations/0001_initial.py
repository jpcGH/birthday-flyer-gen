from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BirthdayFlyer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('celebrant_name', models.CharField(max_length=120)),
                ('birthday_date', models.DateField()),
                ('wish', models.TextField(blank=True)),
                ('theme', models.CharField(choices=[('royal_gold', 'Royal Gold'), ('purple_grace', 'Purple Grace'), ('burgundy_joy', 'Burgundy Joy')], default='royal_gold', max_length=20)),
                ('uploaded_photo', models.ImageField(upload_to='uploads/')),
                ('generated_flyer', models.ImageField(blank=True, upload_to='generated_flyers/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
