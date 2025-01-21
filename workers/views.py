# views.py (add to your existing views)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, timedelta
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Worker, WorkerAssignment, Attendance, Payment, LoanAdjustment
from .serializers import (
    WorkerSerializer,
    WorkerAssignmentSerializer,
    AttendanceSerializer,
    PaymentSerializer,
    LoanAdjustmentSerializer
)


class WorkerViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Worker.objects.all()
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(id_number__icontains=search)
            )
        return queryset

    @action(detail=True, methods=['post'])
    def add_loan(self, request, pk=None):
        worker = self.get_object()
        amount = request.data.get('amount')
        notes = request.data.get('notes', '')

        loan_adjustment = LoanAdjustment.objects.create(
            worker=worker,
            loan_amount=amount,
            notes=notes
        )
        return Response(LoanAdjustmentSerializer(loan_adjustment).data)


class WorkerAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkerAssignment.objects.filter(user=self.request.user)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Attendance.objects.filter(
            assignment__user=self.request.user
        )
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            assignment__user=self.request.user
        )