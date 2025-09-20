from django.core.management.base import BaseCommand
from core_apps.accounts.models import Transaction
from core_apps.accounts.reference_utils import validate_reference_number


class Command(BaseCommand):
    help = "Validates all transaction reference numbers"

    def handle(self, *args, **options):
        transactions = Transaction.objects.all()
        invalid_count = 0

        for transaction in transactions:
            if transaction.reference_number and not validate_reference_number(
                transaction.reference_number
            ):
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid reference number for transaction {transaction.id}: {transaction.reference_number}"
                    )
                )
                invalid_count += 1

        if invalid_count == 0:
            self.stdout.write(self.style.SUCCESS("All reference numbers are valid!"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {invalid_count} transactions with invalid reference numbers"
                )
            )
