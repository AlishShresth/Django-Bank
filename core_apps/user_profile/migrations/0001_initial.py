# Generated by Django 4.2.15 on 2025-08-01 10:56

import cloudinary.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(
                        choices=[("mr", "Mr"), ("mrs", "Mrs"), ("miss", "Miss")],
                        default="mr",
                        max_length=5,
                        verbose_name="Salutation",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                        ],
                        default="male",
                        max_length=8,
                        verbose_name="Gender",
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        default=datetime.date(1900, 1, 1), verbose_name="Date of Birth"
                    ),
                ),
                (
                    "country_of_birth",
                    django_countries.fields.CountryField(
                        default="NP", max_length=2, verbose_name="Country of Birth"
                    ),
                ),
                (
                    "place_of_birth",
                    models.CharField(
                        default="Unknown", max_length=50, verbose_name="Place of Birth"
                    ),
                ),
                (
                    "marital_status",
                    models.CharField(
                        choices=[
                            ("married", "Married"),
                            ("single", "Single"),
                            ("divorced", "Divorced"),
                            ("widowed", "Widowed"),
                            ("separated", "Separated"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        max_length=20,
                        verbose_name="Marital Status",
                    ),
                ),
                (
                    "means_of_identification",
                    models.CharField(
                        choices=[
                            ("drivers_license", "Drivers License"),
                            ("national_id", "National ID"),
                            ("passport", "Passport"),
                            ("citizenship", "Citizenship"),
                        ],
                        default="citizenship",
                        max_length=20,
                        verbose_name="Means of Identification",
                    ),
                ),
                (
                    "id_issue_date",
                    models.DateField(
                        default=datetime.date(2000, 1, 1),
                        verbose_name="ID or Passport Issue Date",
                    ),
                ),
                (
                    "id_expiry_date",
                    models.DateField(
                        default=datetime.date(2024, 1, 1),
                        verbose_name="ID or Passport Expiry Date",
                    ),
                ),
                (
                    "passport_number",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="Passport Number",
                    ),
                ),
                (
                    "nationality",
                    models.CharField(
                        default="Unknown", max_length=30, verbose_name="Nationality"
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        default="+9779812345678",
                        max_length=30,
                        region=None,
                        verbose_name="Phone Number",
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        default="Unknown", max_length=100, verbose_name="Address"
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        default="Unknown", max_length=50, verbose_name="City"
                    ),
                ),
                ("country", models.CharField(default="NP", verbose_name="Country")),
                (
                    "employment_status",
                    models.CharField(
                        choices=[
                            ("self_employed", "Self Employed"),
                            ("employed", "Employed"),
                            ("unemployed", "Unemployed"),
                            ("retired", "Retired"),
                            ("student", "Student"),
                        ],
                        default="self_employed",
                        max_length=20,
                        verbose_name="Employment Status",
                    ),
                ),
                (
                    "employer_name",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Employer Name",
                    ),
                ),
                (
                    "annual_income",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=12,
                        verbose_name="Annual Income",
                    ),
                ),
                (
                    "date_of_employment",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date of Employment"
                    ),
                ),
                (
                    "employer_address",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Employer Address",
                    ),
                ),
                (
                    "employer_city",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Employer City",
                    ),
                ),
                (
                    "employer_state",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Employer State",
                    ),
                ),
                (
                    "photo_url",
                    models.URLField(blank=True, null=True, verbose_name="Photo URL"),
                ),
                (
                    "id_photo",
                    cloudinary.models.CloudinaryField(
                        blank=True, max_length=255, null=True, verbose_name="ID Photo"
                    ),
                ),
                (
                    "id_photo_url",
                    models.URLField(blank=True, null=True, verbose_name="ID Photo URL"),
                ),
                (
                    "signature_photo",
                    cloudinary.models.CloudinaryField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Signature Photo",
                    ),
                ),
                (
                    "signature_photo_url",
                    models.URLField(
                        blank=True, null=True, verbose_name="Signature Photo URL"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="NextOfKin",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(
                        choices=[("mr", "Mr"), ("mrs", "Mrs"), ("miss", "Miss")],
                        max_length=5,
                        verbose_name="Salutation",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=50, verbose_name="First Name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=50, verbose_name="Last Name"),
                ),
                (
                    "other_names",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Other Names"
                    ),
                ),
                ("date_of_birth", models.DateField(verbose_name="Date of Birth")),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                        ],
                        max_length=8,
                        verbose_name="Gender",
                    ),
                ),
                (
                    "relationship",
                    models.CharField(max_length=50, verbose_name="Relationship"),
                ),
                (
                    "email_address",
                    models.EmailField(
                        db_index=True, max_length=254, verbose_name="Email Address"
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, verbose_name="Phone Number"
                    ),
                ),
                ("address", models.CharField(max_length=100, verbose_name="Address")),
                ("city", models.CharField(max_length=50, verbose_name="City")),
                (
                    "country",
                    django_countries.fields.CountryField(
                        max_length=2, verbose_name="Country"
                    ),
                ),
                (
                    "is_primary",
                    models.BooleanField(
                        default=False, verbose_name="Is Primary Next Of Kin"
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="next_of_kin",
                        to="user_profile.profile",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="nextofkin",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_primary", True)),
                fields=("profile", "is_primary"),
                name="unique_primary_next_of_kin",
            ),
        ),
    ]
