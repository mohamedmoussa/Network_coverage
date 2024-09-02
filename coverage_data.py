import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer


class NetworkCoverage:
    def __init__(self, csv_path):
        self.providers = {
            20801: "Orange",
            20810: "SFR",
            20815: "Free",
            20820: "Bouygues"
        }
        self.data = pd.read_csv(csv_path, delimiter=';')
        transformer = Transformer.from_proj(
            proj_from='epsg:2154',
            proj_to='epsg:4326',
            always_xy=True
        )
        self.data['geometry'] = self.data.apply(lambda row: Point(transformer.transform(row['x'], row['y'])), axis=1)
        self.gdf = gpd.GeoDataFrame(self.data, geometry='geometry')
        self.gdf.set_crs(epsg=4326, inplace=True)
        self.gdf_sindex = self.gdf.sindex

    def get_coverage(self, latitude, longitude, radius_km=5):
        point = Point(longitude, latitude)
        radius_deg = radius_km / 111
        buffer = point.buffer(radius_deg)
        possible_matches_index = list(self.gdf_sindex.intersection(buffer.bounds))
        possible_matches = self.gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.geometry.within(buffer)]
        coverage = {}
        for provider_code, provider_name in self.providers.items():
            provider_data = precise_matches[precise_matches['Operateur'] == provider_code]
            if not provider_data.empty:
                coverage[provider_name] = {
                    "2G": bool(provider_data['2G'].any()),
                    "3G": bool(provider_data['3G'].any()),
                    "4G": bool(provider_data['4G'].any())
                }
            else:
                coverage[provider_name] = {
                    "2G": False,
                    "3G": False,
                    "4G": False
                }
        return coverage
