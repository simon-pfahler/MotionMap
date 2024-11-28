import numpy as np
from pyproj import CRS, Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import LineString, Point


class track:

    def __init__(self, points, times):
        """
        Create an object storing a track consisting of multiple sements

        :param points: Coordinates
            For each segment, this is a list of `shapely.geometry.Point`
            objects.
        :param times: Times
            For each segment, this is a list of times from the starting time
            in seconds.
        """
        if len(points) != len(times):
            raise ValueError(
                "Coordinates and times have a different number of segments"
            )
        for i, (ce, te) in enumerate(zip(points, times)):
            if len(ce) != len(te):
                raise ValueError(
                    f"Coordinates and times of segment {i} have a different "
                    "number of points"
                )
        self.points = points
        self.times = np.array(times)

        # >>> obtain projection for the track
        # boundary of the track
        self.aoi = AreaOfInterest(
            north_lat_degree=max([ee.y for e in self.points for ee in e]),
            east_lon_degree=max([ee.x for e in self.points for ee in e]),
            south_lat_degree=min([ee.y for e in self.points for ee in e]),
            west_lon_degree=min([ee.x for e in self.points for ee in e]),
        )

        # CRS for the track
        crs = CRS.from_epsg(
            query_utm_crs_info(datum_name="WGS 84", area_of_interest=self.aoi)[
                0
            ].code
        )

        # projection for the track
        self._projection = Proj(crs, preserve_units=False)
        # <<< obtain projection for the track

    def segments(self):
        """
        Get the number of segments of the track.

        :return: number of segments of the track
        """
        return len(self.times)

    def len(self, segment):
        """
        Get the number of datapoints of a segment.

        :param segment: Index of the considered segment

        :return: number of datapoints of a segment
        """
        return len(self.times[segment])

    def index_at_time(self, segment, time, interpolate=False):
        """
        Get the (interpolated) index of a given time in a segment.

        :param segment: Index of the considered segment
        :param time: Time in seconds from starting time of the segment
        :param interpolate: Whether to interpolate the index or not.
            If `True`, the index of the closest time is returned, if `False`,
            the index is interpolated between the two closest times.
            Defaults to `False`.

        :return: (interpolated) index of the given time in the segment
        """
        index = (np.abs(self.times[segment] - time)).argmin()
        if interpolate == False:
            return index
        if self.times[segment][index] > time:
            index -= 1
        index += (time - self.times[segment][index]) / (
            self.times[segment][index + 1] - self.times[segment][index]
        )
        return index

    def point_at_time(self, segment, time, interpolate=False):
        """
        Get the interpolated coordinates of a given time in a segment.

        :param segment: Index of the considered segment
        :param time: Time in seconds from starting time of the segment
        :param interpolate: Whether to interpolate the coordinates or not.
            If `True`, the `Point` of the closest time is returned, if `False`,
            the `Point` is interpolated between the `Point`s of two closest
            times.
            Defaults to `False`.

        :return: interpolated coordinates of the given time in the segment
        """
        index = (np.abs(self.times[segment] - time)).argmin()
        if interpolate == False:
            return self.points[segment][index]
        if self.times[segment][index] > time:
            index -= 1
        frac = (time - self.times[segment][index]) / (
            self.times[segment][index + 1] - self.times[segment][index]
        )
        ls = LineString(
            [self.points[segment][index], self.points[segment][index + 1]]
        )
        res = ls.interpolate(frac, normalized=True)
        return res

    def proj(self, segment, index):
        """
        Project a point onto a UTM projection

        :param segment: Index of the considered segment
        :param index: Index of the considered point
        """
        return Point(
            self._projection(
                self.points[segment][index].x,
                self.points[segment][index].y,
            )
        )

    def distance(self, segment, start_index=0, end_index=-1):
        """
        Calculate the distance travelled along the track segment between
        `start_index` and `end_index`.

        :param start_index: starting index of the considered track segment
        :param end_index: ending index of the considered track segment

        :return: distance along the track segment
        """
        res = 0
        if start_index < 0:
            start_index = self.len(segment) + start_index
        if end_index < 0:
            end_index = self.len(segment) + end_index
        for index in range(start_index, end_index):
            ls = LineString(
                [self.proj(segment, index + 1), self.proj(segment, index)]
            )
            res += ls.length
        return res
