import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from django.contrib.gis.geos import GEOSGeometry
from .models import TreeInventory

def loadcsv(csv_file):
    """
    Cleans CSV data using Pandas and saves/updates records in PostgreSQL.
    """
    # 1. Load data
    df = pd.read_csv(csv_file)

    # 2. Cleaning Logic (Your original logic)
    df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
    df['SPECIES_NAME'] = df['SPECIES_NAME'].str.title()
    df.loc[df['ROAD_NAME'].isnull(), 'ROAD_NAME'] = 'UnNamed'

    # 3. Filter missing data (Validation)
    dfTemp = df.drop(columns=['OVT_ID', 'LU_HMD', 'ROAD_NAME'], errors='ignore')
    missing_df = df[dfTemp.isna().any(axis=1) | (dfTemp == '').any(axis=1)]
    df_import = df[~df['OBJECTID'].isin(missing_df['OBJECTID'])].copy()

    # 4. GeoPandas Conversion (HK 1980 to WGS84)
    df_import['geometry'] = df_import.apply(lambda row: Point(row['EASTING'], row['NORTHING']), axis=1) 
    gdf = gpd.GeoDataFrame(df_import, geometry='geometry', crs=2326).to_crs(4326)
    
    # 5. Database Loop
    import_count = 0
    for _, row in gdf.iterrows():
        # Convert Shapely Point to Django GEOSGeometry
        pnt = GEOSGeometry(row['geometry'].wkt, srid=4326)
        
        # update_or_create prevents duplicates based on OBJECTID
        TreeInventory.objects.update_or_create(
            objectid=row['OBJECTID'],
            defaults={
                'tree_id': row.get('TREE_ID'),
                'species_name': row.get('SPECIES_NAME'),
                'road_name': row.get('ROAD_NAME'),
                'dbh': row.get('DBH'),
                'height': row.get('HEIGHT'),
                'spread': row.get('SPREAD'),
                'veg_id': row.get('VEG_ID'),
                'lu_hm': row.get('LU_HMD'),
                'easting': row['EASTING'],
                'northing': row['NORTHING'],
                'geometry': pnt,
            }
        )
        import_count += 1
        
    return import_count, len(missing_df)