from django.db import models

# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    projector = models.BooleanField()
    other_features = models.TextField(null=True)


class Reservation(models.Model):
    reservation_date = models.DateField()
    comment = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
