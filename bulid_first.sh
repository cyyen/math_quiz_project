#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt





# Convert static asset files
python manage.py collectstatic --no-input



#first input dbdata

#Create tables without migration:

python manage.py migrate --run-syncdb
# Open Django shell, then exclude ContentType data:

python3 manage.py shell
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
quit()

#Load data:
python3 manage.py loaddata data.json


# Apply any outstanding database migrations
python manage.py migrate
