import json
from urllib.parse import unquote, urlencode
from random import randint
from math import log, sqrt



class Point(object):
    """This class is used for measuring distances between points"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def distance_to(self, other):
        """Returns the Euclidean distance between a pair of given points"""
        return sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def move(self, distance):
        """Moves a point by a given (x, y) tuple amount"""
        self.x += distance[0]
        self.y += distance[1]
        return self.__repr__()


def calc_weighted_popularity(distance_dict, points):
    # Calculate the popularity of a segment, weighted by distance from start
    data = json.loads(points)
    for pin in data['features']:
        pin['properties']['distance'] = distance_dict[pin['properties']['seg_id']][0]
        pin['properties']['weighted_popularity'] = distance_dict[pin['properties']['seg_id']][1]

    return json.dumps(data)


def calculate_distances(json_string):
    """Calculates the distance between two adjacent points, drops those that are too close in order to prevent reverse
       geocoding issue when passed to Google Maps app"""
    waypoint_data = json.loads(json_string)
    waypoint_array = [[float(point['location']['lat']), float(point['location']['lng'])] for point in waypoint_data]
    spaced_array = []
    for i in range(len(waypoint_array) - 1):
        for j in range(i+1, i+2):
            point1 = Point(waypoint_array[i][0], waypoint_array[i][1])
            point2 = Point(waypoint_array[j][0], waypoint_array[j][1])
            print("Point 1: {}, Point 2: {} -- distance: {}".format(point1, point2, point1.distance_to(point2) * 1000))
            if point1.distance_to(point2) * 1000 > 0.001:
                if not waypoint_array[i] in spaced_array:
                    spaced_array.append(waypoint_array[i])
                if not waypoint_array[j] in spaced_array:
                    spaced_array.append(waypoint_array[j])
    print("Not cleaned yet: {}".format(waypoint_array))
    print()
    print("Cleaned for routing: {}".format(spaced_array))
    return spaced_array

def build_maps_URL(start, json_string, spaced_points):
    """Create a Google Maps URL for phone use from calculated waypoints"""
    waypoint_data = json.loads(json_string)
    spaced_waypoints = []
    start_data = json.loads(start)

    spaced_lats = [point[0] for point in spaced_points]
    spaced_lngs = [point[1] for point in spaced_points]

    for point in waypoint_data:
        if float(point['location']['lat']) in spaced_lats and float(point['location']['lng']) in spaced_lngs:
            spaced_waypoints.append(point)
            spaced_lats.remove(float(point['location']['lat']))
            spaced_lngs.remove(float(point['location']['lng']))

    # Convert start data to string
    start_string = '{},{}'.format(start_data['lat'], start_data['lng'])
    base_url = "https://www.google.com/maps/dir/?api=1&"
    waypoints_string = ""
    for point in spaced_waypoints:
        make_unique = str(randint(0, 99999))
        waypoints_string += '{}{},{}{}|'.format(point['location']['lat'], make_unique, point['location']['lng'], make_unique)
    # Remove last "|" at end of string
    waypoints_string = waypoints_string[:-1]

    payload = {'origin': start_string,
               'destination': start_string,
                'travelmode': 'walking',
                'waypoints': waypoints_string
               }

    encoded_url = base_url + urlencode(payload)
    # After encoding URL, need to convert back to string for it to work on iOS
    url_string = unquote(encoded_url)
    print(url_string)
    return url_string

def make_heatmap_csv(strava_geojson):
    """Multiplies points according to total attempts. Used for building homepage heatmap"""
    with open(strava_geojson) as infile:
        all_attempts = []
        point_data = json.load(infile)
        print(len(point_data['features']))
        for point in point_data['features']:
            if not point['properties']['attempts'] == None and not point['properties']['attempts'] == 0:
                # Normalize by log base 3 so dataset fits within Fusion Table 100k records limit
                counter = int(log(point['properties']['attempts'], 3))
                while counter >= 0:
                    all_attempts.append(point)
                    counter -= 1
            else:
                point['properties']['attempts'] = 0
                all_attempts.append(point)
        point_data['features'] = all_attempts
        print(len(point_data['features']))
    with open('all_attempts_points.geojson', 'w') as outfile:
        json.dump(point_data, outfile)

if __name__ == "__main__":
    make_heatmap_csv('strava_api/strava.geojson')
