from django.db import models


class SpotType(models.Model):
    """ The type of Spot.
    """
    name = models.SlugField(max_length=50)


class SpotAvailableHours(models.Model):
    """
    The hours a Spot is available, i.e. the open or closed hours for the
    building the spot is located in.
    """

    day = models.CharField(max_length=9)

    start_time = models.TimeField()
    end_time = models.TimeField()


class SpotExtendedInfo(models.Model):
    """
    Additional institution-provided metadata about a spot. If providing custom
    metadata, you should provide a validator for that data, as well.
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=255)


class SpotImage(models.Model):
    """
    An image of a Spot. Multiple images can be associated with a Spot,
    and Spot objects have a 'Spot.spotimage_set' method that will return all
    SpotImage objects for the Spot.
    """

    image_id = models.IntegerField()
    url = models.CharField(max_length=255)
    description = models.CharField(max_length=200, blank=True)
    display_index = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    creation_date = models.DateTimeField()
    modification_date = models.DateTimeField()
    upload_user = models.CharField(max_length=40)
    upload_application = models.CharField(max_length=100)

    def json_data_structure(self):
        return {
            "id": self.pk,
            "url": self.rest_url(),
            "content-type": self.content_type,
            "width": self.width,
            "height": self.height,
            "creation_date": self.creation_date.isoformat(),
            "modification_date": self.modification_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            # "thumbnail_root": reverse('spot-image-thumb',
            #                           kwargs={'spot_id': self.spot.pk,
            #                                   'image_id': self.pk}
            #                           ).rstrip('/'),
            "description": self.description,
            "display_index": self.display_index
        }


class Spot(models.Model):
    """ Represents a place for students to study.
    """
    spot_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=True)
    uri = models.CharField(max_length=255)
    thumbnail_root = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    height_from_sea_level = models.DecimalField(max_digits=11,
                                                decimal_places=8,
                                                null=True,
                                                blank=True)
    building_name = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=25, blank=True)
    building_description = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    display_access_restrictions = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=50, blank=True)
    manager = models.CharField(max_length=50, blank=True)
    etag = models.CharField(max_length=40)
    last_modified = models.DateTimeField()
    external_id = models.CharField(max_length=100,
                                   null=True,
                                   blank=True,
                                   default=None,
                                   unique=True)

    def json_data_structure(self):
        """
        Get a dictionary representing this spot which can be JSON encoded
        """
        extended_info = {}
        info = self.extended_info
        for attr in info:
            extended_info[attr.key] = attr.value

        available_hours = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': [],
        }

        hours = sorted(self.spot_availability, key=lambda x: x.start_time)
        for window in hours:
            available_hours[window.get_day_display()].append(
                window.json_data_structure())

        images_set = sorted(self.images, key=lambda x: x.display_index)
        images = [img.json_data_structure() for img in images_set]

        types = [t.name for t in self.spot_types]

        checkout_items = [item.json_data_structure() for item in
                          self.items]

        spot_json = {
            "id": self.spot_id,
            # "uri": self.rest_url(),
            "etag": self.etag,
            "name": self.name,
            "type": types,
            "location": {
                # If any changes are made to this location dict,
                # MAKE SURE to reflect those changes in the
                # location_descriptors list in views/schema_gen.py
                "latitude": self.latitude,
                "longitude": self.longitude,
                "height_from_sea_level": self.height_from_sea_level,
                "building_name": self.building_name,
                "floor": self.floor,
                "room_number": self.room_number,
            },
            "capacity": self.capacity,
            "display_access_restrictions":
                self.display_access_restrictions,
            "images": images,
            "available_hours": available_hours,
            "organization": self.organization,
            "manager": self.manager,
            "extended_info": extended_info,
            "items": checkout_items,
            "last_modified": self.last_modified.isoformat(),
            "external_id": self.external_id
        }
        return spot_json


class SpotItem(models.Model):
    item_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255)

    def json_data_structure(self):
        extended = {}

        for i in self.extended_info:
            extended[i.key] = i.value

        images = []

        for image in self.images:
            images.append(image.json_data_structure())

        data = {
            'id': self.item_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'extended_info': extended,
            'images': images
        }

        return data


class ItemImage(models.Model):
    image_id = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    display_index = models.PositiveIntegerField(null=True, blank=True)
    width = models.IntegerField()
    height = models.IntegerField()
    content_type = models.CharField(max_length=40)
    creation_date = models.DateTimeField(auto_now_add=True)
    upload_user = models.CharField(max_length=40)
    upload_application = models.CharField(max_length=100)

    def json_data_structure(self):
        return {
            "id": self.image_id,
            # "url": self.rest_url(),
            "content-type": self.content_type,
            "creation_date": self.creation_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            # "thumbnail_root": reverse('item-image-thumb',
            #                           kwargs={'item_id': self.item.pk,
            #                                   'image_id': self.pk}
            #                           ).rstrip('/'),
            "description": self.description,
            "display_index": self.display_index,
            "width": self.width,
            "height": self.height
        }
