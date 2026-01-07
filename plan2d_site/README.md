# plan2d_site - 2D House Plans Website

A professional Django project for selling 2D house plans with a freemium model.

## Project Structure

```
plan2d_site/
├── apps/                  # All Django apps
│   ├── core/             # Core functionality
│   ├── plans/            # House plans catalog
│   ├── seo/              # SEO management
│   └── orders/           # Order processing
├── config/               # Project configuration
│   ├── settings/
│   │   ├── base.py      # Base settings
│   │   ├── dev.py       # Development settings
│   │   └── prod.py      # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/            # Global templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploads
└── manage.py
```

## Setup Instructions

1. **Activate virtual environment** (if not already active):
   ```bash
   .venv\Scripts\activate
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the application**:
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Admin credentials: `admin` / `admin123` (change in production!)

## Environment Settings

- **Development**: Uses `config.settings.dev` (default)
- **Production**: Switch to `config.settings.prod` by setting `DJANGO_SETTINGS_MODULE`

## Apps Overview

- **core**: Common functionality, public pages (Home, About, FAQ, Contact)
- **plans**: House plan catalog with models (Category, Plan, PlanImage) and admin interface
- **seo**: SEO meta tags, sitemaps, structured data (to be implemented)
- **orders**: Order processing and payment integration (to be implemented)

## Key Features

- ✅ Clean, scalable project structure
- ✅ Split settings (base/dev/prod)
- ✅ SEO-first architecture
- ✅ Professional public pages (Home, About, FAQ, Contact)
- ✅ Complete data models for house plans management
- ✅ Engineer-optimized Django admin interface
- ✅ Freemium model support (free preview + paid plans)
- ✅ Professional folder organization

## Next Steps

1. ~~Implement models in each app~~ ✅ Plans app models complete
2. Create public views for browsing plans
3. Implement plan detail pages
4. Set up payment integration
5. Implement SEO features (sitemaps, structured data)
6. Add plan download tracking
7. Configure production database (PostgreSQL)
8. Set up deployment pipeline

## Documentation

- **URL Structure**: See [URL_STRUCTURE.md](URL_STRUCTURE.md)
- **Plans App**: See [PLANS_APP_DOCUMENTATION.md](PLANS_APP_DOCUMENTATION.md)

## Notes

- All apps are in the `apps/` directory for better organization
- Settings are split for different environments
- No authentication system included yet (add when needed)
- SQLite database for development (switch to PostgreSQL for production)
