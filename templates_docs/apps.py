"""
Templates and documents app configuration.
"""

from django.apps import AppConfig


class TemplatesDocsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'templates_docs'
    verbose_name = 'Templates & Documents'