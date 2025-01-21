# serializers.py
from rest_framework import serializers
from .models import Worker, WorkerAssignment, Attendance, Payment, LoanAdjustment


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'loan_balance')

class WorkerAssignmentSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.full_name', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)

    class Meta:
        model = WorkerAssignment
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class AttendanceSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='assignment.worker.full_name', read_only=True)
    job_type = serializers.CharField(source='assignment.get_job_type_display', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='assignment.worker.full_name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class LoanAdjustmentSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.full_name', read_only=True)

    class Meta:
        model = LoanAdjustment
        fields = '__all__'
        read_only_fields = ('id', 'created_at')