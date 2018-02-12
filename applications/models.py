from django.db import models

from djgeojson.fields import PolygonField

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.core.urlresolvers import reverse

from rpas.models import Rpas

from maps.models import GeofenceLocations
from django.utils import timezone
from datetime import datetime, date, timedelta

from .validators import validate_start_date
from django.core.exceptions import ValidationError

from django.utils.safestring import mark_safe


from .logs import mission_planner_logs


class LogsUpload(models.Model):
    name = models.CharField(max_length=240)
    geom  = gis_models.GeometryField(blank=True, null=True)
    log = models.FileField(upload_to='mission-planner-logs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        from django.contrib.gis.geos import LineString, MultiLineString
        super(LogsUpload,self).save(*args,**kwargs)
        if self.log:
            url = self.log.path
            DATA =  mission_planner_logs(url)
            line = LineString(DATA)
            multi_line = MultiLineString(line)
            self.geom = multi_line

        super(LogsUpload,self).save(*args,**kwargs)



class ReserveAirspace(gis_models.Model):

    geom    = gis_models.PolygonField()
    objects = gis_models.GeoManager()
    rpas    = models.ForeignKey(Rpas)
    date_created  = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    start_day  = models.DateField(default=date.today, validators=[validate_start_date])
    start_time = models.TimeField( help_text='HH:MM:SS')
    end        = models.TimeField(help_text='HH:MM:SS')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    PENDING = 0
    DENIED = 1
    APPROVED = 2
    STATUS = (
        (PENDING,"PENDING"),
        (DENIED,"DENIED"),
        (APPROVED, "APPROVED"),
    )
    application_number = models.CharField(max_length = 255, blank=True, null=True)
    status = models.IntegerField(default=0,choices=STATUS, blank=True, null=True)
    reason = models.CharField(max_length = 255, blank=True, null=True, help_text='If Rejected: Reason for Rejecting')
    comments = models.TextField(blank=True, null=True, help_text='Additional Comments, if any ')
    centroid = gis_models.PointField(blank=True,null=True)



    def save(self, *args, **kwargs):
        self.centroid = self.geom.centroid
        if self.created_by.userprofile.organization.organization_type == 'ROC':
            x = "FP/KCAA/ROC/"
            y = self.pk
            self.application_number = x + str(y)


        elif self.created_by.userprofile.organization.organization_type == 'REC':
            x = "FP/KCAA/REC/"
            y = self.pk
            self.application_number = x + str(y)

        elif self.created_by.userprofile.organization.organization_type == 'PVT':
            x = "FP/KCAA/PVT/"
            y = self.pk
            self.application_number = x + str(y)

        elif self.created_by.userprofile.organization.organization_type == 'ATO':
            x = "FP/KCAA/ATO/"
            y = self.pk
            self.application_number = x + str(y)

        super(ReserveAirspace,self).save(*args,**kwargs)


    def clean(self):
        super(ReserveAirspace, self).clean()
        if self.start_time and self.end:
            booking_time = datetime.combine(date.min, self.end) - datetime.combine(date.min, self.start_time)
            c = booking_time.total_seconds()
            if (c/3600) > 3:
                raise ValidationError('Cannot book airspace for more three hours!')
            elif (c/3600) < 0:
                raise ValidationError("Cmon man!! You can not start a flight at " '{:%H:%M:%S}'.format(self.start_time)  +  " and then GO BACK IN TIME to "  + '{:%H:%M:%S}'.format(self.end) + " to end your flight")

            booking_schedule = datetime.combine(self.start_day, self.start_time) - datetime.now()
            d = booking_schedule.total_seconds()
            if (d/3600) < 4:
                four_hours_from_now = datetime.now() + timedelta(hours=4)
                raise ValidationError("Cannot book airspace less than four hours to take-off! Try from " '{:%H:%M:%S}'.format(four_hours_from_now) )

        if self.geom:
            reserve_qs = ReserveAirspace.objects.all().exclude(pk=self.pk).filter(geom__intersects=self.geom)
            geo_qs     = GeofenceLocations.objects.filter(geom__intersects=self.geom)
            if reserve_qs or geo_qs :
                e = []
                for qs in reserve_qs:
                    error = str(qs.start_day)
                    e.append(error)

                for qs in geo_qs:
                    error = str(qs.name)
                    e.append(error)

                raise ValidationError(
                    ((mark_safe('Cannot book airspace in this zone!!'+
                    "You have violed the folowing Airspace(s)" + '<br> '
                    + str(e) + '<br> ' + '<a href="/applications/airspace/">Go To Airspace</a>')))

                                    )
            x = self.geom.area* 12365.1613
            # geom_area = loc_obj.area_ * 12365.1613 * 10**6
            if x > 9:
                raise ValidationError('This Airspace is greater than the recommended value of 9sq km')


    def dist_from_airports(self):
        dis = GeofenceLocations.objects.all()
        fin = {}
        for x in dis:
            y = self.centroid.distance(x.centroid)/111 *10000
            if y<15:
                fin.update({x.name: y})
        return fin

    def get_area(self):
        x = self.geom.area * 12365.1613
        return x   #sq km

    def get_perimeter(self):
        x = self.geom.length

        return x*111


    def printme(self):
        print('me')


    def __str__(self):
    	return str(self.start_day)

    def get_start_datetime(self):
        booking_schedule = datetime.combine(self.start_day, self.start_time)
        return booking_schedule

    def get_absolute_url(self):
        return reverse("view_airspace")

    @property
    def get_rpas(self):
        return str(self.rpas.rpas_model.model_name)

    @property
    def get_name(self):
        return "%s %s" % (self.created_by.first_name, self.created_by.last_name)

    @property
    def get_phone_number(self):
        return str(self.created_by.userprofile.phone_number)

    @property
    def get_organization(self):
        return str(self.created_by.userprofile.organization.organization_details.name)

    @property
    def get_rpas_pic(self):
        return str(self.rpas.rpas_pic.url)

    @property
    def get_start_day(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        natural_day = naturalday(self.start_day)
        return str(natural_day)