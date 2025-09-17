from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core_apps.accounts.models import BankAccount
from core_apps.common.models import TimeStampedModel, SoftDeleteModel


User = get_user_model()


class VirtualCard(TimeStampedModel, SoftDeleteModel):
    class CardStatus(models.TextChoices):
        ACTIVE = ("active", _("Active"))
        INACTIVE = ("inactive", _("Inactive"))
        BLOCKED = ("blocked", _("Blocked"))
    
    class CardType(models.TextChoices):
        DEBIT = ("debit", _("Debit"))
        CREDIT = ("credit", _("Credit"))

    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="virtual_cards"
    )
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.DO_NOTHING, related_name="virtual_cards"
    )
    card_type = models.CharField(max_length=10, choices=CardType.choices, default=CardType.DEBIT)
    card_number = models.CharField(max_length=16, unique=True)
    expiry_date = models.DateTimeField()
    cvv = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10, choices=CardStatus.choices, default=CardStatus.ACTIVE
    )

    def __str__(self):
        return f"Virtual Card {self.card_number} for {self.user.full_name}"

    @property
    def debit_cards_count(self):
        return self.user.virtual_cards.filter(card_type=self.CardType.DEBIT, status=self.CardStatus.ACTIVE).count()

    @property
    def credit_cards_count(self):
        return self.user.virtual_cards.filter(card_type=self.CardType.CREDIT, status=self.CardStatus.ACTIVE).count()