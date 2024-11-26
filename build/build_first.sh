#!/bin/bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input
#Create tables without migration:

python manage.py migrate --run-syncdb
# Open Django shell, then exclude ContentType data:

# python3 manage.py shell
# from django.contrib.contenttypes.models import ContentType
# ContentType.objects.all().delete()
# quit()

#Load data:
python manage.py loaddata build/data.json

