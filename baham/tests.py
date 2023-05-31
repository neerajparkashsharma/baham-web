from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from baham.models import Vehicle, VehicleModel, Contract, UserProfile
from django.core.exceptions import ValidationError


class BahamConstraintsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='xyz', password='123123')
        self.user_profile = UserProfile.objects.create(user=self.user, birthdate='1990-01-01', gender='M', type='User',
                                                       primary_contact='12345678901', landmark='near xyz',
                                                       town='Mithi')
        self.vehicle_model = VehicleModel.objects.create(
            vendor='Toyota', model='Corolla')

        self.vehicle = Vehicle.objects.create(registration_number='ABC123', model=self.vehicle_model,
                                              colour='black', owner=self.user, status='Active')

    #test-1: one vehicle per owner
    def test_one_vehicle_per_owner(self):
        with self.assertRaises(IntegrityError):
            Vehicle.objects.create(registration_number='ABC123', model=self.vehicle_model,
                                   colour='white', owner=self.user, status='Active')

    #test-2: No more passengers than the vehicle’s sitting capacity
    def test_no_more_companions_than_capacity(self):
        contract = Contract.objects.create(vehicle=self.vehicle, companion=self.user_profile,
                                           effective_start_date='2023-01-01', expiry_date='2023-12-31',
                                           is_active=True, fuel_share=50, maintenance_share=50,
                                           schedule='Daily', created_by=self.user)

        vehicle_capacity = self.vehicle.model.capacity
        for i in range(vehicle_capacity):
            print(f"Adding companion {i+1}...")
            Contract.objects.create(vehicle=self.vehicle, companion=self.user_profile,
                                    effective_start_date='2023-01-01', expiry_date='2023-12-31',
                                    is_active=True, fuel_share=50, maintenance_share=50,
                                    schedule='Daily', created_by=self.user)

        num_companions = Contract.objects.filter(vehicle=self.vehicle).count()
        print(f"Number of companions after adding: {num_companions}")

        try:
            print("Trying to add one more companion...")
            Contract.objects.create(vehicle=self.vehicle, companion=self.user_profile,
                                    effective_start_date='2023-01-01', expiry_date='2023-12-31',
                                    is_active=True, fuel_share=50, maintenance_share=50,
                                    schedule='Daily', created_by=self.user)
        except ValueError as e:
            print(f"Caught ValueError: {e}")
            raise

        num_companions_after = Contract.objects.filter(
            vehicle=self.vehicle).count()
        print(
            f"Number of companions after additional attempt: {num_companions_after}")

    #test-3: Total share cannot exceed 100.
    def test_total_share_cannot_exceed_100(self):
        with self.assertRaises(ValidationError):
            Contract.objects.create(
                vehicle=self.vehicle,
                companion=self.user_profile,
                effective_start_date='2023-01-01',
                expiry_date='2023-12-31',
                is_active=True,
                fuel_share=0,
                maintenance_share=40,
                schedule='Daily',
                created_by=self.user
            )

        with self.assertRaises(ValidationError):
            Contract.objects.create(
                vehicle=self.vehicle,
                companion=self.user_profile,
                effective_start_date='2023-01-01',
                expiry_date='2023-12-31',
                is_active=True,
                fuel_share=50,
                maintenance_share=60,
                schedule='Daily',
                created_by=self.user
            )

        contract = Contract.objects.create(
            vehicle=self.vehicle,
            companion=self.user_profile,
            effective_start_date='2023-01-01',
            expiry_date='2023-12-31',
            is_active=True,
            fuel_share=50,
            maintenance_share=50,
            schedule='Daily',
            created_by=self.user
        )
        self.assertIsNotNone(contract)

    #test-4: Companions cannot have multiple active contracts simultaneously.
    def test_companion_no_multiple_active_contracts(self):
        Contract.objects.create(vehicle=self.vehicle, companion=self.user_profile,
                                effective_start_date='2023-01-01', expiry_date='2023-12-31',
                                is_active=True, fuel_share=50, maintenance_share=50,
                                schedule='Daily', created_by=self.user)

        with self.assertRaises(ValidationError):
            Contract.objects.create(vehicle=self.vehicle, companion=self.user_profile,
                                    effective_start_date='2023-01-01', expiry_date='2023-12-31',
                                    is_active=True, fuel_share=50, maintenance_share=50,
                                    schedule='Daily', created_by=self.user)
