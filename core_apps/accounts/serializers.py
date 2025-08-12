from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
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
