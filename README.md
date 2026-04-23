# RCCG City of Refuge Birthday Flyer Generator

A premium, church-appropriate Django web application for creating beautiful birthday flyers for members of **Redeemed Christian Church of God (RCCG), City of Refuge Parish**.

## Features

- Elegant and responsive Bootstrap 5 UI.
- Form-based flyer generation workflow.
- Input validation for name, date, photo type, image size, and message length.
- Pillow-powered flyer rendering (real image generation, not screenshots).
- Optional celebratory theme selector.
- Default church birthday prayer used automatically when wish is empty.
- Flyer preview and PNG download.
- Flyer records stored for traceability.

## Tech Stack

- Django
- Django Templates
- HTML/CSS/JavaScript
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
│   └── css/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone and enter project directory**
   ```bash
   git clone <repo_url>
   cd birthday-flyer-gen
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start server**
   ```bash
   python manage.py runserver
   ```

6. **Open app**
   Visit `http://127.0.0.1:8000/`

## Media Settings

The app stores:
- Uploaded photos in `media/uploads/`
- Generated flyers in `media/generated_flyers/`

`config/settings.py` includes media settings and `config/urls.py` serves media files in development (`DEBUG=True`).

## How Flyer Generation Works

1. User submits celebrant details + photo.
2. Form validates required fields and image safety constraints.
3. Data is saved in `BirthdayFlyer` model.
4. `flyer_app/utils.py`:
   - Creates gradient premium background.
   - Places celebrant image in circular gold frame.
   - Renders heading, church name, celebrant name/date, and wish text.
   - Wraps long wishes and supports long names.
   - Saves final PNG to `media/generated_flyers/`.
5. Result page displays preview and download button.

## Assumptions

- The app runs in development mode with SQLite.
- A system font is available; utility gracefully falls back to default PIL font when needed.
- Church logo is optional and can be wired by passing a path into `generate_birthday_flyer`.

## Admin (Optional)

Create superuser:
```bash
python manage.py createsuperuser
```
Then visit `/admin` to inspect generated flyer records.
