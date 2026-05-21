"""Apply Python 3.14 compatibility patch for Django Context.__copy__."""
from django.template.context import Context


def _patched_context_copy(self):
    from django.template.context import Context as ContextClass
    duplicate = ContextClass.__new__(ContextClass)
    duplicate.dicts = self.dicts[:]
    if hasattr(self, 'autoescape'):
        duplicate.autoescape = self.autoescape
    if hasattr(self, '_is_secure'):
        duplicate._is_secure = self._is_secure
    return duplicate


Context.__copy__ = _patched_context_copy
