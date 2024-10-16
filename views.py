from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from hospital.models import Doctor
from .models import Appointment
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import razorpay
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'doctors': Doctor.objects.all()
        }
        return render(request, "appointment/index.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')

        # Create a new appointment record
        appointment = self.create_appointment(name, phone, email, doctor_id, date, time, note)

        # Process payment
        payment_result = self.process_payment(appointment)

        # Display success message and redirect to the same page
        messages.success(request, 'Appointment done successfully')
        doctors = Doctor.objects.all()
        return render(request, "appointment/index.html", {'doctors': doctors, 'payment_result': payment_result})

    def create_appointment(self, name, phone, email, doctor_id, date, time, note):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        appointment = Appointment.objects.create(
            name=name, phone=phone, email=email, doctor=doctor, date=date, time=time, note=note
        )
        return appointment

    def process_payment(self, appointment):
        # Initialize Razorpay client with your actual key and secret
        razorpay_client = razorpay.Client(auth=("rzp_test_gpoTDCndtoqFA8", "Hecho1UMboTifxlXgfOC6MCK"))


        # Create a new order in Razorpay
        order_amount = 100  # Set your desired order amount
        order_currency = 'INR'
        order_receipt = f'order_receipt_{appointment.doctor.id}_{appointment.id}'  # Unique order receipt identifier

        order_data = {
            'amount': order_amount,
            'currency': order_currency,
            'receipt': order_receipt,
            'payment_capture': 1  # Auto-capture payment after creation
        }

        razorpay_order = razorpay_client.order.create(order_data)
        print(order_data)
        # Update the appointment record with the Razorpay order ID
        appointment.razorpay_order_id = razorpay_order['id']
        appointment.save()
        
        # Return necessary payment data for template
        payment_result = {
            'order_id': razorpay_order['id'],
            'amount': order_amount,
            'currency': order_currency,
            'razorpay_key': "rzp_test_gpoTDCndtoqFA8",  # Your Razorpay key
        }

        return payment_result

@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, **kwargs):
    subject = 'New Appointment'
    message = f'Hi Admin,\n\nA new appointment has been made.\n\nDetails:\nName: {instance.name}\nPhone: {instance.phone}\nEmail: {instance.email}\nDoctor: {instance.doctor}\nDate: {instance.date}\nTime: {instance.time}\nNote: {instance.note}'
    from_email = 'rushipatil8530@gmail.com'
    to_email = 'rushikeshpawar638@gmail.com' 

    send_mail(subject, message, from_email, [to_email], fail_silently=True)
