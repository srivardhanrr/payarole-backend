import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class Worker(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact = models.CharField(validators=[phone_regex], max_length=17)
    id_type = models.CharField(max_length=50)  # Aadhar, PAN, etc.
    id_number = models.CharField(max_length=50)
    address = models.TextField()
    dob = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    profile_photo = models.ImageField(upload_to='worker_photos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_type}: {self.id_number})"

    def add_loan(self, amount):
        self.loan_balance += amount
        self.save()

    def adjust_loan(self, amount):
        self.loan_balance -= amount
        self.loan_balance = max(0, self.loan_balance)  # Ensure it doesn't go negative
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['id_type', 'id_number']),
            models.Index(fields=['city', 'state'])
        ]


class WorkerAssignment(models.Model):
    JOB_TYPES = [
        ('MAID', 'House Maid'),
        ('COOK', 'Cook'),
        ('CLEAN', 'Cleaning Staff'),
        ('GUARD', 'Security Guard'),
        ('DRIVER', 'Driver'),
        ('OTHER', 'Other')
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TERMINATED', 'Terminated')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    job_type = models.CharField(max_length=10, choices=JOB_TYPES)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    duties = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.full_name} - {self.get_job_type_display()} for {self.user.full_name}"

    class Meta:
        indexes = [
            models.Index(fields=['worker', 'user', 'status']),
            models.Index(fields=['user', 'status'])
        ]


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('LEAVE', 'On Leave')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(WorkerAssignment, on_delete=models.PROTECT)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assignment.worker.full_name} - {self.date} - {self.get_status_display()}"

    class Meta:
        unique_together = ['assignment', 'date']
        indexes = [
            models.Index(fields=['assignment', 'date']),
            models.Index(fields=['date', 'status'])
        ]


class Payment(models.Model):
    PAYMENT_MODES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('BANK', 'Bank Transfer'),
        ('OTHER', 'Other')
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(WorkerAssignment, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Full salary amount
    actual_paid_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount after loan deduction
    payment_date = models.DateField()
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ₹{self.actual_paid_amount} to {self.assignment.worker.full_name} on {self.payment_date}"

    def save(self, *args, **kwargs):
        if not self.actual_paid_amount:
            self.actual_paid_amount = self.amount
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['assignment', 'payment_date']),
            models.Index(fields=['payment_date', 'status'])
        ]


class LoanAdjustment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)  # New loan given
    deduction_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount deducted from salary
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.loan_amount > 0:
            return f"Loan of ₹{self.loan_amount} given to {self.worker.full_name}"
        return f"Loan deduction of ₹{self.deduction_amount} from {self.worker.full_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            # If new loan is given
            if self.loan_amount > 0:
                self.worker.add_loan(self.loan_amount)

            # If deduction from salary
            if self.deduction_amount > 0:
                self.worker.adjust_loan(self.deduction_amount)
                # Update actual paid amount in payment if payment exists
                if self.payment:
                    self.payment.actual_paid_amount = self.payment.amount - self.deduction_amount
                    self.payment.save()

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['worker', 'created_at']),
            models.Index(fields=['payment', 'worker'])
        ]
