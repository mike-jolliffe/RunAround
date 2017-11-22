from secret_keys import TOKEN
import requests
import polyline
import json
from math import sqrt


class Getter:
    """This class is used for making API calls to different Strava endpoints, decoding point data in response,
    and joining data received from different endpoints into a single object"""
    def __init__(self, endpoint):
        self.url = 'https://www.strava.com/api/v3/' + endpoint
        self.response = []

    def get_data(self, **kwargs):
        """Send API request to Strava endpoint"""
        package = {k: v for k, v in kwargs.items()}
        package = {k: ','.join(v) if isinstance(v, list) else v for k, v in package.items()}
        headers = {"Authorization": "Bearer {}".format(TOKEN)}
        resp = requests.get(self.url, params=package, headers=headers)


        self.response.append(resp.json())

    def decode_poly(self):
        """Decode an encoded polyline to point data"""
        for tile in self.response:
            for seg in tile['segments']:
                seg['points'] = polyline.decode(seg['points'])

    @staticmethod
    def to_file(data):
        """Write json data to file"""
        with open('strava.txt', 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def join_on_id(base_set, add_set):
        """Combine dictionaries on segment id"""

        for segment in base_set:
            segment['attempts'] = add_set[segment['id']]

        return base_set

def point_mesh(lower_left_pos, upper_right_pos, points_per_side):
    """
    Create a point mesh within a parent bounding box

    :param lower_left_pos: [lat, lon] of bottom left bounding box corner of a parent box
    :param upper_right_pos: [lat, lon] of upper right bounding box corner of a parent box
    :param num_boxes: total number of boxes to generate within the parent box
    :return: list of bounding boxes, e.g., [[lat, lon, lat, lon], [lat, lon, lat, lon]]
    """

    # Get the total distance to travel between parent box edges
    lat_total = upper_right_pos[0] - lower_left_pos[0]
    lon_total = upper_right_pos[1] - lower_left_pos[1]

    # Get the distance between individual points
    lat_dist = lat_total / (points_per_side + 1)
    lon_dist = lon_total / points_per_side

    # Track the current location during point generation
    lat_curr = lower_left_pos[0]
    lon_curr = lower_left_pos[1]

    point_pairs = []

    while upper_right_pos[0] - lat_curr >= 0:
        while upper_right_pos[1] - lon_curr >= 0:
            point_pairs.append([lat_curr, lon_curr])
            lon_curr += lon_dist
        lon_curr = lower_left_pos[1]
        lat_curr += lat_dist

    return point_pairs

def to_bounding_boxes(point_mesh):
    """
    Converts a point mesh into bounding boxes
    :param point_mesh: a list of [lat, lon] point pairs
    :return: a list of all [lat, lon, lat, lon] bounding boxes created by point mesh
    """

    same_row = point_mesh[0][0]

    all_rows = []
    single_row = []
    # Break point mesh into ten, 10-box rows. I.e., left-right point pairs delineating box left/right
    for row in range(len(point_mesh) - 1):
        for next_to in range(row + 1, row + 2):
            if point_mesh[next_to][0] == same_row:
                single_row.append([point_mesh[row], point_mesh[next_to]])
            else:
                same_row = point_mesh[next_to][0]
                all_rows.append(single_row)
                single_row = []
                break


    # Combine adjacent point rows into "bbox" rows. I.e., top-bottom point pairs delineating box top/bottom
    bbox_rows = []
    for row_i in range(len(all_rows) - 1):
        for row_i2 in range(row_i + 1, row_i + 2):
            bbox_rows.append([all_rows[row_i], all_rows[row_i2]])

    # Zip values in adjacent bbox rows into full boxes
    boxes = []
    for row in bbox_rows:
        for i, j in zip(row[0], row[1]):
            boxes.append([i, j])

    # Get just the lower left and upper right points, and flatten lists
    clean_boxes = []
    for box in boxes:
        clean_boxes.append([str(box[0][0][0]), str(box[0][0][1]), str(box[1][1][0]), str(box[1][1][1])])

    return clean_boxes

if __name__ == '__main__':
    # Pass in bounding box and number of breaks per side (e.g., 20 would make 400 boxes)
    boxes = to_bounding_boxes(point_mesh([45.44, -122.76], [45.60, -122.39], 20))
    # Get and parse all segments data into points
    segments = Getter('segments/explore')
    for box in boxes:
        segments.get_data(bounds=box, activity_type='running')
    print(len(segments.response))
    segments.decode_poly()

    # Get all associated efforts
    all_efforts = []
    for tile in segments.response:
        all_segs = [seg['id'] for seg in tile['segments']]
        effort_dict = {}
        for i_seg in all_segs:
            efforts = Getter('segments/{}'.format(i_seg))
            efforts.get_data()
            for effort in efforts.response:
                popularity = effort.get('effort_count')
                effort_dict[i_seg] = popularity
            # print("{id} -- Efforts: {count}".format(id=i_seg, count=popularity))
        # print(effort_dict)
        combined = segments.join_on_id(tile['segments'], effort_dict)
        all_efforts.extend(combined)
    segments.to_file(all_efforts)

