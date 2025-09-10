#!/usr/bin/env python
"""
Check which dependencies are missing
"""

dependencies = [
    'django',
    'rest_framework',  # djangorestframework import name
    'decouple',        # python-decouple import name
    'rest_framework_simplejwt',
    'corsheaders',     # django-cors-headers import name
    'MySQLdb',         # mysqlclient import name
    'requests',
]

missing = []
available = []

for dep in dependencies:
    try:
        __import__(dep)
        available.append(dep)
    except ImportError:
        missing.append(dep)

print("Available dependencies:")
for dep in available:
    print(f"  ✓ {dep}")

print("\nMissing dependencies:")
for dep in missing:
    print(f"  ✗ {dep}")

if missing:
    print(f"\nTo install missing dependencies, run:")
    print("pip install python-decouple djangorestframework djangorestframework-simplejwt django-cors-headers mysqlclient requests")
else:
    print("\nAll core dependencies are available!")
