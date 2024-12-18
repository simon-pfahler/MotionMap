import networkx as nx
import numpy as np
from pyproj import CRS, Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


class Track:

    def __init__(self, graphs):
        """
        Create an object storing a track consisting of multiple sements

        :param graphs: Graphs of the track
            This is a list of networkx `Graph`s for each track segment
        """
        self.graphs = graphs

        # >>> obtain projection for the track
        # boundary of the track
        self.bbox = [
            min([g.nodes[i]["pos"][0] for g in self.graphs for i in g.nodes]),
            max([g.nodes[i]["pos"][1] for g in self.graphs for i in g.nodes]),
            max([g.nodes[i]["pos"][0] for g in self.graphs for i in g.nodes]),
            min([g.nodes[i]["pos"][1] for g in self.graphs for i in g.nodes]),
        ]
        aoi = AreaOfInterest(*self.bbox)

        # CRS for the track
        crs = CRS.from_epsg(
            query_utm_crs_info(datum_name="WGS 84", area_of_interest=aoi)[
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
        return len(self.graphs)

    def len(self, segment):
        """
        Get the number of datapoints of a segment.

        :param segment: Index of the considered segment

        :return: number of datapoints of a segment
        """
        return len(self.graphs[segment])

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
        times = np.array([node["time"] for node in self.graphs[segment].nodes])
        index = (np.abs(times - time)).argmin()
        if interpolate == False:
            return index
        if self.graphs[segment].nodes[index]["time"] > time:
            index -= 1
        index += (time - self.graphs[segment].nodes[index]["time"]) / (
            self.graphs[segment].nodes[index + 1]["time"]
            - self.graphs[segment].nodes[index]["time"]
        )
        return index

    def node_at_time(self, segment, time, interpolate=False):
        """
        Get the (interpolated) node of a given time in a segment.

        :param segment: Index of the considered segment
        :param time: Time in seconds from starting time of the segment
        :param interpolate: Whether to interpolate the node or not.
            If `False`, the `Node` of the closest time is returned, if `True`,
            the `Node` is interpolated between the `Node`s of two closest
            times.
            Defaults to `False`.

        :return: (interpolated) node of the given time in the segment
        """
        times = np.array([node["time"] for node in self.graphs[segment].nodes])
        index = (np.abs(times - time)).argmin()
        if interpolate == False:
            return self.graphs[segment].nodes[index]
        if self.graphs[segment].nodes[index]["time"] > time:
            index -= 1
        prev_node = self.graphs[segment].nodes[index]
        next_node = self.graphs[segment].nodes[index + 1]
        frac = (time - prev_node["time"]) / (
            next_node["time"] - prev_node["time"]
        )
        interp_index = index + frac
        interp_pos = (
            prev_node["pos"][i]
            + frac * (next_node["pos"][i] - prev_node["pos"][i])
            for i in range(2)
        )
        return interp_index, {"pos": interp_pos, "time": time}

    def utm(self, segment, index):
        """
        Project a `Node`'s pos onto a UTM projection

        :param segment: Index of the considered segment
        :param index: Index of the considered point
        """
        if "utm" not in self.graphs[segment].nodes[index].keys():
            self.graphs[segment].nodes[index]["utm"] = self._projection(
                *self.graphs[segment].nodes[index]["pos"]
            )
        return self.graphs[segment].nodes[index]["utm"]

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
            utm_start = np.array(self.utm(segment, index))
            utm_end = np.array(self.utm(segment, index + 1))
            res += np.linalg.norm(utm_end - utm_start)
        return res
