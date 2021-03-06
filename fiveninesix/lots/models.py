import os

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.files import File
from django.db.models import Q

from elaphe import barcode

from settings import FILE_UPLOAD_TEMP_DIR, BASE_URL

class Lot(models.Model):
    objects = models.GeoManager()

    address = models.CharField(max_length=256, null=True, blank=True)
    borough = models.CharField(max_length=32, null=True, blank=True)
    bbl = models.CharField(max_length=32, db_index=True)
    block = models.CharField(max_length=32)
    lot = models.CharField(max_length=32)
    zipcode = models.CharField(max_length=16, null=True, blank=True)

    owner = models.ForeignKey('Owner', null=True, blank=True)
    owner_contact = models.ForeignKey(
        'OwnerContact', null=True, blank=True,
        help_text=("The person representing the lot's owner who should be "
                   "contacted about this lot.")
    )

    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area_acres = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    school_district = models.CharField(max_length=16, null=True, blank=True)
    community_district = models.CharField(max_length=16, null=True, blank=True)
    city_council_district = models.CharField(max_length=16, null=True, blank=True)
    fire_comp = models.CharField(max_length=16, null=True, blank=True)
    health_area = models.CharField(max_length=16, null=True, blank=True)
    health_ctr = models.CharField(max_length=16, null=True, blank=True)
    police_precinct = models.CharField(max_length=16, null=True, blank=True)
    assess_land = models.IntegerField(null=True, blank=True)
    assess_total = models.IntegerField(null=True, blank=True)
    exempt_land = models.IntegerField(null=True, blank=True)
    exempt_total = models.IntegerField(null=True, blank=True)

    is_vacant = models.BooleanField(default=True)
    actual_use = models.CharField(max_length=128, null=True, blank=True)
    group_has_access = models.BooleanField(default=False)
    accessible = models.BooleanField(default=True, help_text="there is access to the lot from the street or from an adjacent lot with access to the street")

    centroid = models.PointField(null=True)
    centroid_source = models.CharField(max_length=32, null=True, blank=True)
    polygon = models.MultiPolygonField(null=True, blank=True)

    qrcode = models.ImageField(upload_to='qrcodes', null=True, blank=True)

    def __unicode__(self):
        return self.bbl

    @models.permalink
    def get_absolute_url(self):
        return ('lots.views.details', (), { 'bbl': self.bbl })

    def generate_qrcode(self, force=False):
        if self.qrcode and not force:
            return

        url = BASE_URL + self.get_absolute_url()
        lot_code = barcode('qrcode', url, options={ 'version': 3 }, scale=5, margin=10, data_mode='8bits')

        temp_file_path = os.sep.join((FILE_UPLOAD_TEMP_DIR, 'qrcode.%s.png' % self.bbl))
        
        f = open(temp_file_path, 'wb')
        lot_code.save(f, 'png')
        f = open(temp_file_path, 'rb')
        self.qrcode.save(self.bbl + '.png', File(f))
        self.save()

class ExtendedDetails(models.Model):
    """
    Extra details found looking at IPIS and Local Law 48 data.
    """
    lot = models.OneToOneField(Lot)

    parcel_name = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text='Included in Local Law 48 and IPIS'
    )

    number_of_buildings = models.IntegerField(
        null=True,
        blank=True,
        help_text='Should always be 0 if the lot is vacant, but Local Law 48 and IPIS include it'
    )

    primary_use = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='Primary use from IPIS data'
    )
    rpad_description = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='RPAD description from IPIS data'
    )
    jurisdiction_code = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text='Jurisdiction code from IPIS data'
    )
    jurisdiction_description = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='Jurisdiction description from IPIS data'
    )
    is_waterfront = models.NullBooleanField(
        null=True,
        blank=True,
        help_text='From IPIS data'
    )
    is_urban_renewal = models.NullBooleanField(
        null=True,
        blank=True,
        help_text='From IPIS data'
    )

    law_48_address = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text='Address from Local Law 48 data'
    )
    current_uses = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='Current uses from Local Law 48 data'
    )
    has_open_petroleum_spill = models.NullBooleanField(
        null=True,
        blank=True,
        help_text='From Local Law 48 data'
    )
    agency_codes = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='In Local Law 48 data'
    )
    historic_district = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='From Local Law 48 data'
    )
    landmark = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='From Local Law 48 data'
    )

class Owner(models.Model):
    name = models.CharField(max_length=256)
    person = models.CharField(max_length=128, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    site = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    type = models.ForeignKey('OwnerType', null=True, blank=True)
    code = models.CharField(max_length=8, null=True, blank=True)

    def __unicode__(self):
        return self.name

class OwnerContact(models.Model):
    """
    A contact for an Owner. Overrides the contact information in the Owner 
    when present.
    """
    owner = models.ForeignKey(Owner)

    name = models.CharField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    jurisdiction = models.TextField(
        null=True, blank=True,
        help_text=("The part of the city this contact covers (eg, Queens, "
                   "northern Brooklyn).")
    )
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.owner.name)

class OwnerType(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class Alias(models.Model):
    lot = models.ForeignKey('Lot')
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return '%s -> %s' % (self.name, self.lot.bbl)

class LotGroup(models.Model):
    name = models.CharField(max_length=256)
    lots = models.ManyToManyField(Lot)

class Review(models.Model):
    """
    A (manual) review of a Lot that gives us more details than we got from the city's data.
    """
    lot = models.ForeignKey(Lot)
    reviewer = models.ForeignKey(User, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    
    in_use = models.BooleanField(blank=False, null=False, default=False, help_text="the lot is not fenced, is being used")
    actual_use = models.CharField(blank=True, null=True, max_length=128, help_text="eg, 'garden' or 'parking'")
    accessible = models.BooleanField(blank=False, null=False, default=True, help_text="there is access to the lot from the street or from an adjacent lot (or community garden) with access to the street")
    needs_further_review = models.BooleanField(blank=False, null=False, default=False, help_text="should be visited on foot or double-checked by someone else (please state why in notes)")

    nearby_lots = models.TextField(blank=True, null=True, help_text="BBLs of nearby/adjacent vacant lots that might be used in coordination with this lot")

    hpd_plans = models.NullBooleanField('HPD plans', blank=True, null=True, help_text="does HPD have open RFPs or other development plans for this lot?")
    hpd_plans_details = models.TextField('HPD plans details', blank=True, null=True, help_text="details about HPD's plans for this lot, if any")

    should_be_imported = models.NullBooleanField(blank=True, null=True, help_text="data should be added to the respective lot")
    imported = models.BooleanField(blank=False, null=False, default=False, help_text="data has been added to the respective lot")

LOT_QUERIES = {
    'vacant': Lot.objects.filter(
        Q(
            accessible=True,
            is_vacant=True,
            group_has_access=False,
            organizer=None,
            owner__type__name='city'
        ) & ~Q(actual_use='gutterspace')
    ),
    'garden': Lot.objects.filter(
        actual_use__startswith='Garden',
        owner__type__name='city'
    ),
    'private_accessed': Lot.objects.filter(
        owner__type__name='private',
        group_has_access=True
    ),
    'organizing': Lot.objects.exclude(organizer=None, owner__type__name='city'),
    'accessed': Lot.objects.filter(group_has_access=True, owner__type__name='city'),
    'inaccessible': Lot.objects.filter(accessible=False, owner__type__name='city'),
    'gutterspace': Lot.objects.filter(Q(accessible=False) | Q(actual_use='gutterspace')),
}

LOT_QS = {
    'vacant': 
        Q(
            accessible=True,
            is_vacant=True,
            group_has_access=False,
            organizer=None,
            owner__type__name='city'
        ) & ~Q(actual_use='gutterspace'),
    'garden': Q(
        actual_use__startswith='Garden',
        owner__type__name='city'
    ),
    'private_accessed': Q(
        owner__type__name='private',
        group_has_access=True
    ),
    'organizing': ~Q(organizer=None, owner__type__name='city'),
    'accessed': Q(group_has_access=True, owner__type__name='city'),
    'inaccessible': Q(accessible=False, owner__type__name='city'),
    'gutterspace': Q(accessible=False) | Q(actual_use='gutterspace'),
}
