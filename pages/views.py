from django.shortcuts import render, redirect
from django.http import JsonResponse
from pages.models import Segment
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from pages.helpers import calculate_distances, calc_weighted_popularity, build_maps_URL
#from pages.strava_api.secret_keys import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER # This is for localhost
from django.core.serializers import serialize
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']


def home(request):
    """Renders homepage"""
    return render(request, 'home.html')

def map(request):
    """Renders maps page, passing in context grabbed from home.html"""
    if request.method == "POST":

        lng = float(request.POST.get('lon'))
        lat = float(request.POST.get('lat'))
        mileage = request.POST.get('mileage')
        if not mileage == '':
            radius = float(mileage) / 3
        else:
            radius = 1.0
        starting_point = Point(lng, lat)

        print(radius)
        all_points = Segment.objects.filter(geom__distance_lt=(starting_point, D(mi=radius)))

        pin_dict = {}
        for pin in all_points.values():
            distance = starting_point.distance(pin['geom']) * 100
            popularity = pin['attempts']
            # Inverse distance weighting of popularity based on proximity to origin
            weighted_popularity = (popularity / distance ** 2)
            pin_dict[pin['seg_id']] = [distance, weighted_popularity]
            #print("Distance: {}, Popularity: {}, Weighted Popularity: {}".format(distance, popularity, weighted_popularity))

        all_points = serialize('geojson', all_points, geometry_field='geom')


        route_points = calc_weighted_popularity(pin_dict, all_points)

        return render(request, 'maps.html', {'curr_lng': lng, 'curr_lat': lat, 'mileage': mileage, 'route_points': route_points})

    return JsonResponse({'error': 'Please try again with params'})


def phone(request):
    """Handles text messaging run route to phone"""
    if request.method == "POST":
        start = request.POST.get('start')
        print(start)
        phone_num = request.POST.get('phone')
        waypoints = request.POST.get('waypoints')
        spaced_points = calculate_distances(waypoints)
        url_msg = build_maps_URL(start, waypoints, spaced_points)

        twilio_client = Client(TWILIO_ACCOUNT_SID,
                               TWILIO_AUTH_TOKEN)
        twilio_client.messages.create(body=url_msg, to=phone_num,
                                           from_=TWILIO_NUMBER)

        return redirect('home')

