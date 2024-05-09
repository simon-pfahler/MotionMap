import gpxpy

def read_gpx(filename):
    gpx_f = open(filename, 'r')
    gpx = gpxpy.parse(gpx_f)
    
    coords = [list() for _ in range(len(gpx.tracks))]
    for i in range(len(gpx.tracks)):
        for segment in gpx.tracks[i].segments:
            for j in range(len(segment.points)):
                point = segment.points[j]
                coords[i].append({"x": point.longitude, "y": point.latitude})

    return coords
