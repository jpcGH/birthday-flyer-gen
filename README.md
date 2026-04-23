# RCCG City of Refuge Birthday Flyer Generator

A premium Django web app for **Redeemed Christian Church of God (RCCG), City of Refuge Parish** to create church-appropriate birthday flyers with a modern editor and PNG export.

## Highlights

- Premium editor layout:
  - Left: form controls
  - Right: **fully live flyer preview**
- Instant preview updates for:
  - celebrant name
  - birthday date
  - custom wish
  - uploaded photo
  - selected theme
- Three distinct themes:
  - **Royal Grace**
  - **Refuge Light**
  - **Covenant Bloom**
- Pillow-powered server-side PNG generation (exportable/downloadable)
- Safe validations for image type/size and message length
- Responsive UI built with Django templates + Bootstrap + vanilla JavaScript

## Tech Stack

- Django
- Django Templates
- HTML/CSS/JavaScript (vanilla)
- Bootstrap 5
- Pillow
- SQLite (development)

## Project Structure

```
birthday-flyer-gen/
├── config/
├── flyer_app/
├── media/
│   ├── generated_flyers/
│   └── uploads/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations
   ```bash
   python manage.py migrate
   ```

4. Run development server
   ```bash
   python manage.py runserver
   ```

5. Open `http://127.0.0.1:8000/`

## Media Handling

- Uploaded photos: `media/uploads/`
- Generated flyers: `media/generated_flyers/`

`config/settings.py` and `config/urls.py` are configured for development media serving when `DEBUG=True`.

## Generation Workflow

1. User edits celebrant details in the form.
2. Live preview updates instantly in-browser (no submit needed).
3. User submits form to generate final flyer.
4. Django validates input and saves model data.
5. Pillow renders flyer PNG with matching layout/theme.
6. Result page shows generated flyer and download button.

## Notes

- If wish is empty, a default RCCG-styled birthday prayer is used.
- Font loading gracefully falls back to PIL default when system fonts are unavailable.
- Optional logo support exists in flyer utility via `church_logo_path`.
