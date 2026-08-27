import base64
import csv
import os
import sys
from io import StringIO
from time import time

import requests

from source.map_to_streets import *
from source.plot import *
from source.read_gpx import *
from source.street_network import *
from source.track import *
from source.utility import *

name = "NAME"

api_key = "DUMMY"

headers = {
    "Authorization": f"Basic {base64.b64encode(f'API_KEY:{api_key}'.encode()).decode()}"
}

overview_url = f"https://intervals.icu/api/v1/athlete/0/activities.csv"


def activity_url(activity_id):
    return f"https://intervals.icu/api/v1/activity/{activity_id}/gpx-file?power=false&hr=false"


print(f"Fetching activity list")
response = requests.get(overview_url, headers=headers)
response.raise_for_status()

rows = list(csv.DictReader(StringIO(response.text)))

activity_types = {"Run", "Walk", "Hike", "TrailRun"}

activity_ids = [
    row["\ufeffid"] for row in rows if row["type"] in activity_types
]

os.makedirs(f"mapped_activities_{name}", exist_ok=True)

nr_mapped_activities = len(os.listdir(f"mapped_activities_{name}"))

print(
    f"Found {len(activity_ids)} activities, of which "
    f"{len(activity_ids)-nr_mapped_activities} are new!"
)

obtained_graph = nx.Graph()

for activity_id in activity_ids:

    if os.path.exists(f"mapped_activities_{name}/activity_{activity_id}.gpx"):
        continue

    print(f"Mapping activity {activity_id}")

    response = requests.get(activity_url(activity_id), headers=headers)
    response.raise_for_status()

    with open(f"/tmp/activity_{activity_id}.gpx", "wb") as f:
        f.write(response.content)

    track = Track(read_gpx(f"/tmp/activity_{activity_id}.gpx")).filled(20)

    print(f"\tTrack has {track.len(0)} nodes")

    street_network = Street_network(track.bbox)

    print(f"\tStreet network has {street_network.nr_edges()} edges")

    start_time = time()
    mapped_track = map_track_to_street_network(track, street_network)
    end_time = time()

    print(f"\tMapping took {end_time-start_time:.2f}s")

    write_gpx(
        mapped_track.graphs,
        f"mapped_activities_{name}/activity_{activity_id}.gpx",
    )

    os.remove(f"/tmp/activity_{activity_id}.gpx")
