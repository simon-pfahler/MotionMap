import networkx as nx
import osmnx
from pyproj import CRS, Proj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


class street_network:
    def __init__(self, bbox):
        """
        Create an object storing a street network.

        :param bbox: bounding box of the street network
            Tuple of coordinates [west, north, east, south]
        """
        self.bbox = bbox

        self.graph = nx.Graph(
            osmnx.graph_from_bbox(
                (bbox),
                network_type="all",
                simplify=True,
                retain_all=True,
                truncate_by_edge=True,
            )
        )

        # convert 'x' and 'y' keys to 'pos' key storing GPS
        for node in self.graph.nodes.values():
            node["pos"] = (node["x"], node["y"])
            del node["x"], node["y"]

        # >>> obtain projection for the track
        aoi = AreaOfInterest(*self.bbox)

        # CRS for the street network
        crs = CRS.from_epsg(
            query_utm_crs_info(datum_name="WGS 84", area_of_interest=aoi)[
                0
            ].code
        )

        # projection for the track
        self._projection = Proj(crs, preserve_units=False)
        # <<< obtain projection for the track

    def nr_nodes(self):
        """
        Get the number of `Node`s of the street network.

        :return: number of `Node`s of the street network
        """
        return len(self.graph.nodes)

    def nr_edges(self):
        """
        Get the number of `Edge`s of the street network.

        :return: number of `Edge`s of the street network
        """
        return len(self.graph.edges)

    def utm(self, index):
        """
        Project a `Node`'s pos onto a UTM projection

        :param segment: Index of the considered segment
        :param index: Index of the considered point
        """
        if "utm" not in self.graph.nodes[index].keys():
            self.graph.nodes[index]["utm"] = self._projection(
                *self.graph.nodes[index]["pos"]
            )
        return self.graph.nodes[index]["utm"]
