from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core_apps.common.models import TimeStampedModel, SoftDeleteModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger


User = get_user_model()


class BankAccount(TimeStampedModel, SoftDeleteModel):
    class AccountType(models.TextChoices):
        CURRENT = ("current", _("Current"))
        SAVINGS = ("savings", _("Savings"))
        FIXED = ("fixed", _("Fixed"))

    class AccountStatus(models.TextChoices):
        ACTIVE = ("active", _("Active"))
        INACTIVE = ("inactive", _("Inactive"))
        BLOCKED = ("blocked", _("Blocked"))
        PENDING = ("pending", _("Pending"))

    class AccountCurrency(models.TextChoices):
        DOLLAR = ("us_dollar", _("US Dollar"))
        POUND_STERLING = ("pound_sterling", _("Pound Sterling"))
        NEPALESE_RUPEES = ("nepalese_rupees", _("Nepalese Rupees"))

    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="bank_accounts",
    )
    account_number = models.CharField(
        _("Account Number"),
        max_length=20,
        unique=True,
        db_index=True,
    )
    account_balance = models.DecimalField(
        _("Account Balance"),
        decimal_places=2,
        max_digits=10,
        default=0.00,
    )
    currency = models.CharField(
        _("Currency"),
        max_length=20,
        choices=AccountCurrency.choices,
        default=AccountCurrency.NEPALESE_RUPEES,
    )
    account_status = models.CharField(
        _("Account Status"),
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.INACTIVE,
        db_index=True,
    )
    account_type = models.CharField(
        _("Account Type"),
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.SAVINGS,
    )
    is_primary = models.BooleanField(
        _("Primary Account"),
        default=False,
    )
    kyc_submitted = models.BooleanField(
        _("KYC Submitted"),
        default=False,
        db_index=True,
    )
    kyc_verified = models.BooleanField(
        _("KYC Verified"),
        default=False,
        db_index=True,
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="verified_accounts",
    )
    verification_date = models.DateTimeField(
        _("Verification Date"),
        null=True,
        blank=True,
    )
    verification_note = models.TextField(
        _("Verification Notes"),
        blank=True,
    )
    fully_activated = models.BooleanField(
        _("Fully Activated"),
        default=False,
    )
    interest_rate = models.DecimalField(
        _("Interest Rate"),
        max_digits=5,
        decimal_places=4,
        default=0.00,
        help_text=_("Annual interest rate as a decimal (e.g. 0.0150 for 1.50%)"),
    )

    def __str__(self) -> str:
        return f"{self.user.full_name}'s {self.get_currency_display()} - {self.get_account_type_display()} Account - {self.account_number} "

    @property
    def annual_interest_rate(self):
        if self.account_type == self.AccountType.FIXED:
            return Decimal("0.0500")
        if self.account_type != self.AccountType.SAVINGS:
            return Decimal("0.0000")
        return Decimal("0.0275")
        # different interest for different balance
        # balance = self.account_balance
        # if balance < Decimal("100000"):
        #     return Decimal("0.0050")
        # elif Decimal("100000") <= balance < Decimal("500000"):
        #     return Decimal("0.0100")
        # else:
        #     return Decimal("0.0150")

    def apply_daily_interest(self):
        if (
            self.account_type == self.AccountType.SAVINGS
            or self.account_type == self.AccountType.FIXED
        ):
            daily_rate = self.annual_interest_rate / Decimal("365")
            interest = (Decimal(self.account_balance) * daily_rate).quantize(
                Decimal(".01"), rounding=ROUND_HALF_UP
            )
            logger.info(
                f"Applying daily interest {interest} to account {self.account_number}"
            )
            self.account_balance += interest
            self.save()

            Transaction.objects.create(
                user=self.user,
                amount=interest,
                transaction_type=Transaction.TransactionType.INTEREST,
                description="Daily interest applied",
                receiver=self.user,
                receiver_account=self,
                status=Transaction.TransactionStatus.COMPLETED,
            )
            return interest
        return Decimal("0.00")

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        unique_together = ["user", "currency", "account_type"]

    def clean(self) -> None:
        if self.account_balance < 0:
            raise ValidationError(_("Account balance cannot be negative"))

    def save(self, *args, **kwargs) -> None:
        if self.is_primary:
            BankAccount.objects.filter(user=self.user).update(is_primary=False)
        super().save(*args, **kwargs)

    def record_month_end_balance(self):
        """Record the current balance as the month-end balance"""
        from django.utils import timezone
        from calendar import monthrange

        today = timezone.now().date()
        _, last_day = monthrange(today.year, today.month)
        if today.day != last_day:
            logger.info(f"Today ({today}) is not the last day of the month. Skipping.")
            return "Not the last day of the month"
        
        month = today.replace(day=1)
        
        monthly_balance, created = MonthlyBalanceHistory.objects.get_or_create(
            bank_account=self, month=month, defaults={"balance": self.account_balance}
        )

        if not created:
            monthly_balance.balance = self.account_balance
            monthly_balance.save()

        return monthly_balance
    
    @property
    def balance_change_percentage(self):
        """Calculate percentage change compared to previous month"""
        from django.utils import timezone
        from datetime import timedelta
        
        current_month = timezone.now().date().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        
        current_balance = self.account_balance
        
        try:
            previous_balance = self.monthly_balances.get(month=previous_month).balance
        except MonthlyBalanceHistory.DoesNotExist:
            return None
        
        if previous_balance == 0:
            return None
        
        change = current_balance - previous_balance
        percentage_change = (change / previous_balance) * 100
        
        return percentage_change   


class Transaction(TimeStampedModel, SoftDeleteModel):
    class TransactionStatus(models.TextChoices):
        PENDING = ("pending", _("Pending"))
        COMPLETED = ("completed", _("Completed"))
        FAILED = ("failed", _("Failed"))

    class TransactionType(models.TextChoices):
        DEPOSIT = ("deposit", _("Deposit"))
        WITHDRAWAL = ("withdrawal", _("Withdrawal"))
        TRANSFER = ("transfer", _("Transfer"))
        INTEREST = ("interest", _("Interest"))

    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, related_name="transactions"
    )
    amount = models.DecimalField(
        _("Amount"), decimal_places=2, max_digits=12, default=0.00
    )
    description = models.CharField(
        _("Description"), max_length=500, null=True, blank=True
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="received_transactions",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="sent_transactions",
    )
    receiver_account = models.ForeignKey(
        BankAccount,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="received_transactions",
    )
    sender_account = models.ForeignKey(
        BankAccount,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="sent_transactions",
    )
    status = models.CharField(
        choices=TransactionStatus.choices,
        max_length=20,
        default=TransactionStatus.PENDING,
    )
    transaction_type = models.CharField(
        choices=TransactionType.choices,
        max_length=20,
    )

    def __str__(self) -> str:
        return f"{self.transaction_type} - {self.amount} - {self.status}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]


class MonthlyBalanceHistory(TimeStampedModel):
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="monthly_balances"
    )
    balance = models.DecimalField(
        _("Month End Balance"),
        decimal_places=2,
        max_digits=10,
        default=0.00,
    )
    month = models.DateField(_("Month"), db_index=True)

    class Meta:
        verbose_name = _("Monthly Balance History")
        verbose_name_plural = _("Monthly Balance Histories")
        unique_together = ["bank_account", "month"]
        ordering = ["-month"]

    def __str__(self):
        return f"{self.bank_account.account_number} - {self.month.strftime('%Y-%m')}: {self.balance}"
