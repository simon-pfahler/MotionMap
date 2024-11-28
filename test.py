from typing import no_type_check

import matplotlib.pyplot as plt
from pyproj import CRS, Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

from source.plot_track import *
from source.read_gpx import *
from source.track import *

test_track = track(*read_gpx("test_activity.gpx"))

plot_track(test_track)
