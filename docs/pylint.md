# Pylint Report

**Score: 9.77 / 10**

Run with `pylint-django` plugin against `tracker/` and `fittrack/`, excluding auto-generated migrations.

```
python -m pylint tracker/ fittrack/
```

## Remaining Warnings

All remaining warnings are `C0301 line-too-long` in `tracker/management/commands/seed_exercises.py`. These are long string literals in the exercise seed data dictionary and cannot be shortened without breaking the data.

| File | Line | Code | Message |
|------|------|------|---------|
| seed_exercises.py | 13 | C0301 | Line too long (141/120) |
| seed_exercises.py | 14 | C0301 | Line too long (130/120) |
| seed_exercises.py | 15 | C0301 | Line too long (141/120) |
| seed_exercises.py | 16 | C0301 | Line too long (130/120) |
| seed_exercises.py | 17 | C0301 | Line too long (136/120) |
| seed_exercises.py | 18 | C0301 | Line too long (133/120) |
| seed_exercises.py | 19 | C0301 | Line too long (137/120) |
| seed_exercises.py | 20 | C0301 | Line too long (129/120) |
| seed_exercises.py | 21 | C0301 | Line too long (153/120) |
| seed_exercises.py | 22 | C0301 | Line too long (140/120) |
| seed_exercises.py | 23 | C0301 | Line too long (128/120) |
| seed_exercises.py | 24 | C0301 | Line too long (135/120) |
| seed_exercises.py | 25 | C0301 | Line too long (135/120) |
| seed_exercises.py | 26 | C0301 | Line too long (139/120) |
| seed_exercises.py | 27 | C0301 | Line too long (147/120) |
| tracker/admin.py  | 2  | C0301 | Line too long (133/120) |
| tracker/urls.py   | 48 | C0301 | Line too long (121/120) |

## Configuration

Suppressions are managed via `.pylintrc` at the project root. The following checks are disabled as Django false positives:

| Code | Reason |
|------|--------|
| `no-member` | Django ORM manager methods not visible to static analysis |
| `too-few-public-methods` | Django `Meta` inner classes by design |
| `too-many-ancestors` | Django form/model inheritance chain |
| `imported-auth-user` | Direct `User` import is intentional here |
| `broad-exception-caught` | Intentional catch-all in CSV export view |
| `too-many-locals/branches/statements` | Large dashboard view — refactor deferred |
