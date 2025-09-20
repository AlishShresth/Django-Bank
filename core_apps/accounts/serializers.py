from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from decimal import Decimal
from .models import BankAccount, Transaction


class AccountListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(read_only=True)
    annual_interest_rate = serializers.FloatField()
    balance_change_percentage = serializers.FloatField()

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "user",
            "account_number",
            "currency",
            "account_balance",
            "account_status",
            "account_type",
            "kyc_submitted",
            "kyc_verified",
            "fully_activated",
            "is_primary",
            "annual_interest_rate",
            "created_at",
            "balance_change_percentage",
        ]
        read_only_fields = ["id", "account_balance", "created_at"]


class AccountCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    initial_deposit = serializers.DecimalField(
        decimal_places=2, max_digits=10, required=False
    )

    class Meta:
        model = BankAccount
        fields = ["email", "account_type", "initial_deposit", "currency"]

    def validate(self, data: dict) -> dict:
        email = data.get("email")
        account_type = data.get("account_type")
        currency = data.get("currency")

        if not email:
            raise serializers.ValidationError(_("Email is required"))
        if not account_type:
            raise serializers.ValidationError(_("Account type is required"))
        if not currency:
            raise serializers.ValidationError(_("Account currency is required"))

        return data


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


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    sender_account = serializers.CharField(max_length=20, required=False)
    receiver_account = serializers.CharField(max_length=20, required=False)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.1")
    )
    reference_number = serializers.CharField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "reference_number",
            "user",
            "amount",
            "description",
            "receiver",
            "receiver_account",
            "sender",
            "sender_account",
            "transaction_type",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at", "reference_number"]

    def to_representation(self, instance: Transaction) -> str:
        representation = super().to_representation(instance)
        representation["amount"] = str(representation["amount"])
        representation["sender"] = (
            instance.sender.full_name if instance.sender else None
        )
        representation["receiver"] = str(
            instance.receiver.full_name if instance.receiver else None
        )
        representation["sender_account"] = (
            instance.sender_account.account_number if instance.sender_account else None
        )
        representation["receiver_account"] = (
            instance.receiver_account.account_number
            if instance.receiver_account
            else None
        )
        return representation

    def validate(self, data):
        transaction_type = data.get("transaction_type")
        sender_account_number = data.get("sender_account")
        receiver_account_number = data.get("receiver_account")
        amount = data.get("amount")

        try:
            if transaction_type == Transaction.TransactionType.WITHDRAWAL:
                account = BankAccount.objects.get(account_number=sender_account_number)
                data["sender_account"] = account
                data["receiver_account"] = None
                if account.account_balance < amount:
                    raise serializers.ValidationError(
                        _("Insufficient funds for withdrawal")
                    )
            elif transaction_type == Transaction.TransactionType.DEPOSIT:
                account = BankAccount.objects.get(
                    account_number=receiver_account_number
                )
                data["sender_account"] = None
                data["receiver_account"] = account
            else:
                sender_account = BankAccount.objects.get(
                    account_number=sender_account_number
                )
                receiver_account = BankAccount.objects.get(
                    account_number=receiver_account_number
                )
                data["sender_account"] = sender_account
                data["receiver_account"] = receiver_account

                if sender_account == receiver_account:
                    raise serializers.ValidationError(
                        _("Sender and receiver accounts must be different")
                    )
                if sender_account.currency != receiver_account.currency:
                    raise serializers.ValidationError(
                        _("Insufficient funds for transfer")
                    )
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError(_("One or both accounts not found"))
        return data


class SecurityQuestionSerializer(serializers.Serializer):
    security_answer = serializers.CharField(max_length=30)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        if data["security_answer"] != user.security_answer:
            raise serializers.ValidationError("Incorrect security answer.")
        return data


class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        if not user.verify_otp(data["otp"]):
            raise serializers.ValidationError("Invalid or expired OTP")
        return data


class UsernameVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=12)

    def validate_username(self, value: dict) -> dict:
        user = self.context["request"].user
        if user.username != value:
            raise serializers.ValidationError("Invalid username.")
        return value


class AccountDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(read_only=True)
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "user",
            "account_number",
            "currency",
            "account_balance",
            "account_status",
            "account_type",
            "kyc_submitted",
            "kyc_verified",
            "fully_activated",
            "is_primary",
            "interest_rate",
            "created_at",
            "recent_transactions",
        ]
        read_only_fields = ["id", "account_balance", "created_at"]

    def get_recent_transactions(self, obj):
        combined_transactions = list(
            obj.sent_transactions.exclude(transaction_type="interest")
        ) + list(obj.received_transactions.exclude(transaction_type="interest"))
        sorted_transactions = sorted(
            combined_transactions, key=lambda t: t.created_at, reverse=True
        )

        # remove duplicate by ID
        deduped_transactions = {}
        for transaction in sorted_transactions:
            deduped_transactions[transaction.id] = transaction

        # Convert back to list and limit to 5
        result = list(deduped_transactions.values())[:5]
        return TransactionSerializer(result, many=True).data
