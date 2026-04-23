from .models import SiteBranding


def branding(request):
    defaults = SiteBranding.defaults()
    config = SiteBranding.get_active()

    if config:
        defaults.update(
            {
                'site_title': config.site_title,
                'navbar_title': config.navbar_title,
                'footer_owner': config.footer_owner,
                'footer_rights_text': config.footer_rights_text,
                'logo_url': config.logo.url if config.logo else None,
                'logo_path': config.logo.path if config.logo else None,
            }
        )

    return {'branding': defaults}
