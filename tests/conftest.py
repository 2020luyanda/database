"""pytest loads this file first, before any test file.

Importing app.db here runs its libpq.dll fix before any test does `import psycopg`.
"""
import app.db  # noqa: F401
