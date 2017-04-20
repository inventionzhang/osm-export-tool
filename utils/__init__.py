from osm_xml import OSM_XML
from osm_pbf import OSM_PBF
from geopackage import Geopackage
from shp import Shapefile
from kml import KML
from garmin_img import GarminIMG
from osmand_obf import OsmAndOBF

FORMAT_NAMES = {}
for cls in [OSM_XML, OSM_PBF, Geopackage,Shapefile,
            KML,GarminIMG,OsmAndOBF]:
    FORMAT_NAMES[cls.name] = cls

def map_names_to_formats(names_list):
    return [FORMAT_NAMES[name] for name in names_list]
