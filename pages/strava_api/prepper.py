from django.contrib.gis.geos import Point
import json

class Prepper:
    """This class converts dictionary of lat/longs into Point features"""
    def __init__(self, infile):
        self.data = infile
        self.cleaned = None

    def clean_data(self, *args):
        """Eliminates any k,v pairs from dict that aren't given as args in function"""
        clean_data = []
        for segment in self.data:
            clean_dict = {}
            for key in segment:
                if key in args:
                    clean_dict[key] = segment[key]
            clean_data.append(clean_dict)
        self.cleaned = clean_data

    def single_point_test(self):
        """Creates a Point to try and put in database"""
        for segment in self.cleaned:
            for point_pair in segment['points']:
                point = Point(point_pair)
        return point

    def point_by_point(self):
        points_array = []
        for segment in self.cleaned:
            # Normalize number of points to 6 per mile of segment, or for loading heatmap initially, just allow 1000 points
            allowed_pts = 1000#(segment['distance'] / 1600) * 6
            for point in segment['points']:
                if allowed_pts >= 0:
                    points_array.append({'id': segment['id'], 'distance': segment['distance'],
                                         'attempts': segment['attempts'], 'location': point})
                    allowed_pts -= 1
                else:
                    break
        return points_array

    def to_geoJSON(self, point_data):
        """Converts the JSON object to GeoJSON"""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [d["location"][1], d["location"][0]],
                    },
                    "properties": {'id': d['id'],
                    'attempts': d['attempts'],
                    'distance': d['distance']}
                } for d in point_data]
        }
        with open('strava.geojson', 'w') as output:
            json.dump(geojson, output)

if __name__ == '__main__':
    with open('strava.txt') as infile:
        data = json.load(infile)
    cleaner = Prepper(data)
    cleaner.clean_data('id', 'points', 'distance', 'attempts')
    #print(cleaner.single_point_test())
    points = cleaner.point_by_point()
    cleaner.to_geoJSON(points)