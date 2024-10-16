# models.py

from django.db import models
from hospital.models import Doctor

class Appointment(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=10)
    note = models.TextField()
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    # Add your new fields below
    new_field1 = models.CharField(max_length=255, blank=True, null=True)
    new_field2 = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}'s Appointment with Dr. {self.doctor.name}"

