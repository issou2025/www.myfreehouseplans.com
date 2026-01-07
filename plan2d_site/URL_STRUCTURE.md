# URL Structure Reference

## Core Public Pages

All URLs are clean, SEO-friendly, and properly namespaced.

### Available URLs

| Page | URL | View Class | Template |
|------|-----|------------|----------|
| **Home** | `/` | `HomeView` | `core/home.html` |
| **About** | `/about/` | `AboutView` | `core/about.html` |
| **FAQ** | `/faq/` | `FAQView` | `core/faq.html` |
| **Contact** | `/contact/` | `ContactView` | `core/contact.html` |
| **Admin** | `/admin/` | Django Admin | - |

### URL Namespacing

All core URLs use the `core:` namespace:

```python
# In templates
{% url 'core:home' %}
{% url 'core:about' %}
{% url 'core:faq' %}
{% url 'core:contact' %}

# In views
from django.urls import reverse
reverse('core:home')
reverse('core:about')
```

### Views Pattern

All views use class-based `TemplateView`:
- Consistent structure
- Easy to extend with mixins
- Clean and maintainable
- `ContactView` includes POST handling for form submission

### Template Structure

```
templates/
├── base.html                   # Base template with header/footer
└── apps/
    └── core/
        └── templates/
            └── core/
                ├── home.html   # Homepage
                ├── about.html  # About page
                ├── faq.html    # FAQ page
                └── contact.html # Contact page
```

### Navigation

The navigation is automatically highlighted based on the current page using:
```django
{% if request.resolver_match.url_name == 'home' %}active{% endif %}
```

### Content Guidelines (Implemented)

✓ Emphasizes "Human-designed plans"
✓ Mentions Autodesk Revit usage prominently
✓ Professional, construction-oriented language
✓ No AI marketing buzzwords
✓ Clear freemium model explanation
✓ English language only

### Testing URLs

```bash
# Home
http://127.0.0.1:8000/

# About
http://127.0.0.1:8000/about/

# FAQ
http://127.0.0.1:8000/faq/

# Contact
http://127.0.0.1:8000/contact/

# Admin
http://127.0.0.1:8000/admin/
```

### Next Steps (Future Development)

When adding new pages:

1. Add view to `apps/core/views.py` (or appropriate app)
2. Create template in `apps/{app}/templates/{app}/`
3. Add URL pattern to `apps/{app}/urls.py`
4. Update navigation in `templates/base.html` if needed

### Example: Adding a New Page

```python
# views.py
class NewPageView(TemplateView):
    template_name = 'core/newpage.html'

# urls.py
path('newpage/', views.NewPageView.as_view(), name='newpage'),

# base.html
<a href="{% url 'core:newpage' %}">New Page</a>
```
