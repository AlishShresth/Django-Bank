from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from decimal import Decimal
from .models import BankAccount


class AccountVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "kyc_submitted",
            "kyc_verified",
            "verification_date",
            "verification_note",
            "fully_activated",
            "account_status",
        ]
        read_only_fields = ["fully_activated"]

    def validate(self, data: dict) -> dict:
        kyc_verified = data.get("kyc_verified")
        kyc_submitted = data.get("kyc_submitted")
        verification_date = data.get("verification_date")
        verification_note = data.get("verification_note")

        if kyc_verified:
            if not verification_date:
                raise serializers.ValidationError(
                    _("Verification date is required when verifying an account.")
                )
            if not verification_note:
                raise serializers.ValidationError(
                    _("Verification note is required when verifying an account.")
                )
            if kyc_submitted and not all(
                [kyc_verified, verification_date, verification_note]
            ):
                raise serializers.ValidationError(
                    _(
                        "All Verification fields (KYC Verified, verification date and note) must be provided when KYC is submitted"
                    )
                )
        return data


class DepositSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.1")
    )

    class Meta:
        model = BankAccount
        fields = ["account_number", "amount"]

    def validate_account_number(self, value: str) -> str:
        try:
            account = BankAccount.objects.get(account_number=value)
            self.context["account"] = account
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError(_("Invalid account number."))
        return value

    def to_representation(self, instance: BankAccount) -> str:
        representation = super().to_representation(instance)
        representation["amount"] = str(representation["amount"])
        return representation


class CustomerInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    email = serializers.EmailField(source="user.email")
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            "account_number",
            "full_name",
            "email",
            "photo_url",
            "account_balance",
            "account_type",
            "currency",
        ]

    def get_photo_url(self, obj) -> None:
        if hasattr(obj.user, "profile") and obj.user.profile.photo_url:
            return obj.user.profile.photo_url
        return None
