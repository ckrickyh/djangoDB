# pip install geoalchemy2
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from django.contrib.gis.geos import GEOSGeometry
from .models import TreeInventory
from django.db import connection
from sqlalchemy import create_engine
from django.utils import timezone

def loadcsv(csv_path, sep=",", **kwargs):
    """
    Cleans CSV data using Pandas and saves/updates records in PostgreSQL.
    """
    dfTreeInv = pd.read_csv(csv_path, sep=sep)
    rawRows = dfTreeInv.shape[0]
    duplicatedRows = dfTreeInv['TREE_ID'].duplicated().sum()
    dfTreeInv.drop_duplicates(subset=['TREE_ID'], keep='first', inplace=True)
    

    dfTreeInv[dfTreeInv.select_dtypes(['object']).columns] = dfTreeInv.select_dtypes(['object']).apply(lambda x: x.str.strip())
    dfTreeInv = dfTreeInv.drop(columns=['GeometryEasting', 'GeometryNorthing'])   # drop geo east, north
    dfTreeInv['SPECIES_NAME']= dfTreeInv['SPECIES_NAME'].str.title()    #title species name
    dfTreeInv.loc[dfTreeInv['ROAD_NAME'].isnull(), 'ROAD_NAME'] = 'UnNamed'  # fill empty road name by 'UnNamed'

    dfTemp=dfTreeInv.drop(columns=['OVT_ID', 'LU_HMD', 'ROAD_NAME'])
    dfTemp.columns.to_list()

    # Filter out rows with NaN, None, or empty strings
    missing_dfTemp = dfTemp[dfTemp.isna().any(axis=1) | (dfTemp == '').any(axis=1)]
    num_missing = len(set(missing_dfTemp['OBJECTID']))
    missingRows = ', '.join(map(str, sorted(set(missing_dfTemp['OBJECTID']))))

    dfTreeImport = dfTreeInv[~dfTreeInv['OBJECTID'].isin(missing_dfTemp['OBJECTID'])].copy()
    importedRows = dfTreeImport.shape[0]

    # gdf
    dfTreeImport['geometry'] = dfTreeImport.apply(lambda row: Point(row['EASTING'], row['NORTHING']), axis=1) 
    gdfTreeImport = gpd.GeoDataFrame(dfTreeImport, geometry='geometry', crs=2326).to_crs(4326) # change to crs4326 fm 2326
    gdfTreeImport['import_date'] = timezone.now()
    gdfTreeImport.columns =gdfTreeImport.columns.str.lower()
    
    # clear the db 

    # this method delete row by row, too slow, TreeInventory.objects.all().delete()
    # using sql delete is faster

    # clear table data at first
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE treeinvs_treeinventory RESTART IDENTITY CASCADE;")


    # 1. Build the connection string
    # engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    engine = create_engine('postgresql+psycopg2://postgres:admin1234@localhost:5432/erb8dbmanager')
    
    # 2. Use to_postgis instead of to_sql
    gdfTreeImport.to_postgis(
        name='treeinvs_treeinventory', 
        con=engine, 
        if_exists='append',  # do not replace
        index=False,
    )

    return rawRows, importedRows, missingRows, num_missing, duplicatedRows