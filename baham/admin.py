from typing import Any, Optional
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils import timezone
from baham.models import VehicleModel, UserProfile, Vehicle, Contract
from django.contrib.auth.models import User

# Decorator defining which model class to attach with ModelAdmin
@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ("uuid", "vendor", "model", "type", "capacity", "void_reason", "date_created")
    readonly_fields = ("uuid", "date_created", "created_by", "date_updated", "updated_by", "date_voided", "voided_by")
    list_filter = ("vendor", "model", "type", "capacity", "date_created")
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            obj.date_created = timezone.now()
        else:
            obj.updated_by = request.user
            obj.date_updated = timezone.now()
        if obj.voided:
            obj.voided_by = request.user
            obj.date_voided = timezone.now()
        else:
            obj.void_reason = None
            obj.voided_by = None
            obj.date_voided = None
        return super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "gender", "type", "active", "town")
    readonly_fields = ("uuid", "date_created", "created_by", "date_updated", "updated_by", "date_voided", "voided_by")
    list_filter = ("type", "active", "town", "date_created")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            obj.date_created = timezone.now()
        else:
            obj.updated_by = request.user
            obj.date_updated = timezone.now()
        if obj.voided:
            obj.voided_by = request.user
            obj.date_voided = timezone.now()
        else:
            obj.void_reason = None
            obj.voided_by = None
            obj.date_voided = None
        return super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("uuid", "registration_number", "model", "owner", "status")
    readonly_fields = ("uuid", "date_created", "created_by", "date_updated", "updated_by", "date_voided", "voided_by")
    list_filter = ("model", "owner", "status", "date_created")

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        obj.date_updated = timezone.now()
        if obj.voided:
            obj.voided_by = request.user
            obj.date_voided = timezone.now()
        else:
            obj.void_reason = None
            obj.voided_by = None
            obj.date_voided = None
        return super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
