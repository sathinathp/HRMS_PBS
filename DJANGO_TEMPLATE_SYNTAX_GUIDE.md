# Django Template Syntax - Quick Reference Guide

## ✅ Correct Template Tag Spacing

### Comparison Operators
Always use spaces around comparison operators:

```django
<!-- ✓ CORRECT -->
{% if variable == value %}
{% if count != 0 %}
{% if age > 18 %}
{% if score >= 90 %}
{% if price < 100 %}
{% if quantity <= 10 %}

<!-- ✗ INCORRECT -->
{% if variable==value %}
{% if count!=0 %}
{% if age>18 %}
{% if score>=90 %}
{% if price<100 %}
{% if quantity<=10 %}
```

### Logical Operators
```django
<!-- ✓ CORRECT -->
{% if user.is_active and user.is_staff %}
{% if status == 'pending' or status == 'approved' %}
{% if not user.is_banned %}

<!-- ✗ INCORRECT -->
{% if user.is_active and user.is_staff %}  <!-- This is actually correct -->
{% if status=='pending' or status=='approved' %}
```

### Membership Operators
```django
<!-- ✓ CORRECT -->
{% if item in list %}
{% if user not in banned_users %}

<!-- ✗ INCORRECT -->
{% if item in list %}  <!-- This is actually correct -->
```

## Common Template Tag Patterns

### If-Elif-Else
```django
{% if condition1 == value1 %}
    <!-- content -->
{% elif condition2 == value2 %}
    <!-- content -->
{% else %}
    <!-- content -->
{% endif %}
```

### For Loops
```django
{% for item in items %}
    {% if item.status == 'active' %}
        {{ item.name }}
    {% endif %}
{% empty %}
    No items found
{% endfor %}
```

### Filters
```django
<!-- Filters don't need spaces -->
{{ value|default:"N/A" }}
{{ date|date:"Y-m-d" }}
{{ text|truncatewords:30 }}
```

## Template Syntax Errors to Avoid

### 1. Missing Spaces Around Operators
```django
<!-- ✗ ERROR: TemplateSyntaxError -->
{% if month==1 %}

<!-- ✓ CORRECT -->
{% if month == 1 %}
```

### 2. Using Assignment Instead of Comparison
```django
<!-- ✗ ERROR: Invalid syntax -->
{% if status = 'active' %}

<!-- ✓ CORRECT -->
{% if status == 'active' %}
```

### 3. Missing endif/endfor/endblock
```django
<!-- ✗ ERROR: Unclosed tag -->
{% if condition %}
    content
<!-- Missing {% endif %} -->

<!-- ✓ CORRECT -->
{% if condition %}
    content
{% endif %}
```

### 4. Incorrect Variable Access
```django
<!-- ✗ ERROR: Invalid syntax -->
{% if user['name'] == 'John' %}

<!-- ✓ CORRECT -->
{% if user.name == 'John' %}
```

## Testing Template Syntax

### Using Django Shell
```python
python manage.py shell

from django.template import Template, Context

# Test your template
t = Template('{% if month == 1 %}January{% endif %}')
result = t.render(Context({'month': 1}))
print(result)  # Output: January
```

### Using Django Check Command
```bash
python manage.py check
```

### Using Template Validation Script
```bash
python fix_template_spacing.py
```

## IDE Configuration

### VS Code
Install the "Django" extension and add to settings.json:
```json
{
    "files.associations": {
        "*.html": "django-html"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    }
}
```

### PyCharm
1. Go to Settings → Languages & Frameworks → Django
2. Enable Django support
3. Set template language to Django

## Pre-Commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python fix_template_spacing.py
if [ $? -ne 0 ]; then
    echo "Template spacing issues found. Please fix before committing."
    exit 1
fi
```

## Common Patterns in This Project

### Month Selection Dropdown
```django
<select name="month">
    <option value="1" {% if month == 1 %}selected{% endif %}>January</option>
    <option value="2" {% if month == 2 %}selected{% endif %}>February</option>
    <!-- ... -->
</select>
```

### Year Selection Dropdown
```django
<select name="year">
    <option value="2024" {% if year == 2024 %}selected{% endif %}>2024</option>
    <option value="2025" {% if year == 2025 %}selected{% endif %}>2025</option>
</select>
```

### Status Badges
```django
<span class="badge {% if status == 'APPROVED' %}bg-success{% elif status == 'PENDING' %}bg-warning{% else %}bg-danger{% endif %}">
    {{ status }}
</span>
```

## Resources

- [Django Template Language Documentation](https://docs.djangoproject.com/en/stable/ref/templates/language/)
- [Django Template Builtins](https://docs.djangoproject.com/en/stable/ref/templates/builtins/)
- [Common Template Errors](https://docs.djangoproject.com/en/stable/ref/templates/api/#common-template-errors)

---

**Last Updated:** January 8, 2026
**Maintained By:** Development Team
