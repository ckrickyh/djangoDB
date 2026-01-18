# from django.db import models

# Create your models here.
from django.contrib.gis.db import models
from django.utils import timezone

class TreeInventory(models.Model):
    # Identifiers
    objectid = models.IntegerField(unique=True)
    tree_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # general info
    species_name = models.CharField(max_length=255, null=True, blank=True)
    ovt_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Dendrometric variable
    dbh = models.FloatField(null=True, blank=True) # Diameter at Breast Height
    height = models.FloatField(null=True, blank=True)
    spread = models.FloatField(null=True, blank=True)
    
    # Location Info
    road_name = models.CharField(max_length=255, null=True, blank=True)
    veg_id = models.CharField(max_length=100, null=True, blank=True)
    lu_hmd = models.CharField(max_length=50, null=True, blank=True)
    
    #import date
    # import_date = models.DateTimeField(auto_now_add=True)
    import_date = models.DateTimeField(default=timezone.now)

    # The actual PostGIS Geometry field
    # SRID 2326 = HK 1980 Grid System
    geometry = models.PointField(srid=4326)

    # Raw Coordinates (Optional, but good for reference)
    easting = models.FloatField()
    northing = models.FloatField()

    def __str__(self):
        return f"{self.tree_id} - {self.species_name}"

class TreePhotoUrl(models.Model):

    tree_tag = models.ForeignKey(TreeInventory, 
        to_field='tree_id', # This tells Django to link to tree_id
        on_delete=models.PROTECT, 
        db_constraint=False, # This stops the database from checking the ID
        related_name='photos', # allows reverse access from TreeInventory to TreePhoto
        null=False
    )
    url = models.URLField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"Photo for {self.tree_tag_id}"