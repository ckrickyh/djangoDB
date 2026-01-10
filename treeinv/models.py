# from django.db import models

# Create your models here.
from django.contrib.gis.db import models

class TreeInventory(models.Model):
    # Identifiers
    objectid = models.IntegerField(unique=True)
    tree_id = models.CharField(max_length=50, null=True, blank=True)

    # general info
    species_name = models.CharField(max_length=255, null=True, blank=True)
    dovt_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Dendrometric variable
    dbh = models.FloatField(null=True, blank=True) # Diameter at Breast Height
    height = models.FloatField(null=True, blank=True)
    spread = models.FloatField(null=True, blank=True)
    
    # Location Info
    road_name = models.CharField(max_length=255, null=True, blank=True)
    veg_id = models.CharField(max_length=100, null=True, blank=True)
    lu_hm = models.CharField(max_length=50, null=True, blank=True)
    
    # Raw Coordinates (Optional, but good for reference)
    easting = models.FloatField()
    northing = models.FloatField()
    
    # The actual PostGIS Geometry field
    # SRID 2326 = HK 1980 Grid System
    geometry = models.PointField(srid=4326)

    def __str__(self):
        return f"{self.tree_id} - {self.species_name}"