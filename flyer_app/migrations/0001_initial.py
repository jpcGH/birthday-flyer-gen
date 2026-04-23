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
                ('theme', models.CharField(choices=[('royal_grace', 'Royal Grace'), ('refuge_light', 'Refuge Light'), ('covenant_bloom', 'Covenant Bloom')], default='royal_grace', max_length=20)),
                ('uploaded_photo', models.ImageField(upload_to='uploads/')),
                ('generated_flyer', models.ImageField(blank=True, upload_to='generated_flyers/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
