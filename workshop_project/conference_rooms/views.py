from django.shortcuts import render, redirect, HttpResponse
from conference_rooms.models import Room, Reservation
from django.views import View
from django.db.models.functions import Cast
from django.db.models import F
from django.db import models
import datetime
import re
# Create your views here.


def main_page(request):
    rooms = Room.objects.annotate(available=Cast(F'projector', output_field=models.BooleanField()))
    for room in rooms:
        room.available = True
    reservations = Reservation.objects.filter(reservation_date=datetime.date.today())
    if len(reservations) > 0:
        room_ids = []
        for reservation in reservations:
            room_ids.append(reservation.room.id)
        for room in rooms:
            if room.id in room_ids:
                room.available = False
    if request.method == "GET":
        return render(request, 'main.html', context={"rooms": rooms})
    elif request.method == "POST":
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        projector_on = bool(request.POST.get('projector_on'))
        projector_off = bool(request.POST.get('projector_off'))
        available = request.POST.get('available')
        if name:
            rooms = rooms.filter(name__contains=name)
        if capacity:
            rooms = rooms.filter(capacity__gte=capacity)
        if projector_off and not projector_on:
            rooms = rooms.filter(projector=False)
        elif not projector_off and projector_on:
            rooms = rooms.filter(projector=True)
        if available:
            rooms = rooms.filter(available=True)
        return render(request, 'main.html', context={"rooms": rooms})


class AddRoom(View):
    def get(self, request):
        return render(request, 'new_room.html')

    def post(self, request):
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        projector = bool(request.POST.get('projector'))
        other_features = request.POST.get('other_features')
        if name is None or capacity is None or name == "" or capacity == "":
            return HttpResponse(f"""<p>You have to input name and capacity of the room.</p><br><a href="new">Back</a>""")
        rooms = Room.objects.all()
        counter = 0
        for room in rooms:
            if room.name == name:
                return HttpResponse(f"""<p>This room already exists.</p><br><a href="new">Back</a>""")
            counter += 1
        if len(other_features) > 0:
            room_to_create = Room.objects.create(name=name, capacity=capacity, projector=projector, other_features=other_features)
        else:
            room_to_create = Room.objects.create(name=name, capacity=capacity, projector=projector, other_features="")
        return HttpResponse(f'<p>Successfully created {name}.</p><br><a href="../">Back</a>')


def room_details(request, room_id):
    room = Room.objects.get(pk=room_id)
    reservations = Reservation.objects.filter(room=room).order_by('reservation_date')
    return render(request, 'room_details.html', context={"room": room, "reservations": reservations})


def room_edit(request, room_id):
    if request.method == "GET":
        room = Room.objects.get(pk=room_id)
        return render(request, 'edit.html', context={"room": room})
    elif request.method == "POST":
        room = Room.objects.get(pk=room_id)
        name = request.POST.get('name')
        room.name = request.POST.get('name')
        room.capacity = request.POST.get('capacity')
        room.projector = bool(request.POST.get('projector'))
        room.other_features = request.POST.get('other_features')
        rooms = Room.objects.all()
        counter = 0
        for room1 in rooms:
            if room1.name == name:
                return HttpResponse(f"""<p>This room already exists.</p><br><a href="http://127.0.0.1:8000/">Back</a>""")
            counter += 1
        room.save()
        return HttpResponse("""<h3>Successfully changed rooms' information.<a style="font-size:18px;" href="http://127.0.0.1:8000/"><br><br>Home</a></h3>""")


def room_delete(request, room_id):
    if request.method == "GET":
        room = Room.objects.get(pk=room_id)
        return render(request, 'delete.html', context={"room": room})
    elif request.method == "POST":
        message = request.POST.get('message')
        room = Room.objects.get(pk=room_id)
        if message == "Delete":
            room.delete()
            return HttpResponse(f"""<h2>Deleted {room.name}.</h2><br><a href="http://127.0.0.1:8000/">Back</a>""")
        else:
            return HttpResponse(f"""<h2>You entered wrong message!</h2><br><a href="../{room_id}/">Wróć</a>""")


def room_reserve(request, room_id):
    if request.method == "GET":
        room = Room.objects.get(pk=room_id)
        reservations = Reservation.objects.filter(reservation_date__gte=datetime.date.today()).filter(room=room)
        return render(request, 'reserve.html', context={"room": room, "reservations": reservations})
    elif request.method == "POST":
        try:
            reservation_date = datetime.datetime.strptime(request.POST.get('reservation_date'), "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse(f"""<h3>You have to select a date!</h3><br><br><a href="http://127.0.0.1:8000/room/reserve/{room_id}">Back</a><br><br><a href="http://127.0.0.1:8000/">Home</a>""")
        comment = request.POST.get('comment')
        if reservation_date < datetime.date.today():
            return HttpResponse(f"""<h3>You can't make reservations to the past you dumbass...</h3><br><br><a href="http://127.0.0.1:8000/room/reserve/{room_id}">Back</a><br><br><a href="http://127.0.0.1:8000/">Home</a>""")
        room = Room.objects.get(pk=room_id)
        reservation = Reservation.objects.filter(room=room).filter(reservation_date=reservation_date)
        if reservation:
            return HttpResponse(f"""<h3>Room {room.name} is already reserved on {reservation_date}.<br><br></h3><a href="http://127.0.0.1:8000/room/reserve/{room_id}">Back</a><br><br><a href="http://127.0.0.1:8000/">Home</a>""")
        else:
            created_reservation = Reservation.objects.create(reservation_date=reservation_date, comment=comment, room=room)
            return HttpResponse(f"""<h3>Successfully made a reservation!</h3><br><br><a href="http://127.0.0.1:8000/">Home</a>""")
