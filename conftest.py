"""
conftest.py - pytest configuration for FitTrack

Handles:
1. Python 3.14 compatibility patch for Django Context.__copy__
2. Test-specific Django settings (simple staticfiles storage)
"""

import os

# Must be set BEFORE Django imports
os.environ['DJANGO_TESTING'] = '1'

import copy
import django
import pytest
from django.conf import settings as django_settings
from django.template.context import Context


# Monkeypatch Context.__copy__ to work with Python 3.14
def patched_context_copy(self):
    """Patched __copy__ that works with Python 3.14's changes to super()."""
    # Create a new Context instance without calling super()
    from django.template.context import Context as ContextClass
    duplicate = ContextClass.__new__(ContextClass)
    # Copy the attributes manually
    duplicate.dicts = self.dicts[:]
    if hasattr(self, 'autoescape'):
        duplicate.autoescape = self.autoescape
    if hasattr(self, '_is_secure'):
        duplicate._is_secure = self._is_secure
    return duplicate


# Apply the patch before Django initializes
Context.__copy__ = patched_context_copy

# Also register a copy function in Python's copy module dispatch
if hasattr(copy, '_copy_dispatch'):
    def copy_context(context):
        """Custom copier for Context objects."""
        return context.__copy__()
    copy._copy_dispatch[Context] = copy_context


@pytest.fixture(scope="session", autouse=True)
def django_db_setup(django_db_setup, django_db_blocker):
    """Ensure database is set up."""
    with django_db_blocker.unblock():
        pass



