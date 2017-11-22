import os, sys
from RunAround.settings import BASE_DIR

# Set path to settings file
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RunAround.settings')

# Set up django in this file to access django-specific imports
import django
django.setup()

from django.contrib.gis.utils import layermapping
from pages.models import *

# Build data mapping between model and geojson
data_mapping = {
    'seg_id': 'id',
    'attempts': 'attempts',
    'distance': 'distance',
    'geom': 'MULTIPOINT',
}


stravaGeo = os.path.abspath(
    os.path.join(BASE_DIR, 'pages', 'strava_api', 'strava.geojson'),
)

# Insert geojson into database using LayerMapping
def run(verbose=True):
    lm = layermapping.LayerMapping(
        Segment, stravaGeo, data_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

run()