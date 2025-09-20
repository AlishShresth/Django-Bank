import secrets
import string
from datetime import datetime


def generate_transaction_reference(transaction_type: str) -> str:
    """
    Generate a unique transaction reference number.

    Format: TRX{YYMMDD}{type_code}{random_chars}{check_digit}
    - TRX: Fixed prefix
    - YYMMDD: Date part (year, month, day)
    - type_code: 3-letter code for transaction type
    - random_chars: 6 random alphanumeric characters
    - check_digit: Luhn check digit for validation

    Args:
        transaction_type: The type of transaction (deposit, withdrawal, transfer, etc.)

    Returns:
        A unique transaction reference number
    """
    type_codes = {
        "deposit": "DEP",
        "withdrawal": "WDR",
        "transfer": "TRF",
        "interest": "INT",
    }

    date_part = datetime.now().strftime("%y%m%d")

    type_code = type_codes.get(
        transaction_type.lower(), "MISC"
    )  # default to MISC if not found

    alphabet = string.ascii_uppercase + string.digits
    random_chars = "".join(secrets.choice(alphabet) for _ in range(6))

    partial_ref = f"TRX{date_part}{type_code}{random_chars}"

    check_digit = calculate_alphanumeric_check_digit(partial_ref)

    return f"{partial_ref}{check_digit}"


def calculate_alphanumeric_check_digit(reference: str) -> str:
    """
    Calculate a check digit for alphanumeric reference using a modified Luhn algorithm.

    Args:
        reference: The reference string without check digit

    Returns:
        A single character check digit
    """

    # Convert alphanumeric to numeric values (A=10, B=11, ..., Z=35)
    def char_to_value(c):
        if c.isdigit():
            return int(c)
        return 10 + ord(c.upper()) - ord("A")

    # Calculate weighted sum
    total = 0
    for i, char in enumerate(reference):
        value = char_to_value(char)
        # Double every second digit from the right
        if (len(reference) - i) % 2 == 0:
            value *= 2
            # If value is >= 10, sum the digits
            if value >= 10:
                value = (value // 10) + (value % 10)
        total += value

    # Calculate check digit
    check_value = (10 - (total % 10)) % 10

    # Convert back to character (0-9 remain as digits, 10-35 become A-Z)
    if check_value < 10:
        return str(check_value)
    return chr(ord("A") + check_value - 10)


def validate_reference_number(reference: str) -> bool:
    """
    Validate a transaction reference number using its check digit.

    Args:
        reference: The complete reference number including check digit

    Returns:
        True if valid, False otherwise
    """
    if len(reference) < 2:
        return False

    # Separate the reference and check digit
    ref_without_check = reference[:-1]
    check_digit = reference[-1]

    # Calculate expected check digit
    expected_check = calculate_alphanumeric_check_digit(ref_without_check)

    return check_digit == expected_check
