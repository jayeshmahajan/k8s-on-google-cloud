import structlog
import re

# Define masking functions
def mask_credit_card(value):
    return re.sub(r'\b(\d{4})\d{8,12}(\d{4})\b', r'\1********\2', value)

def redact_ssn(value):
    return re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', value)

def email_redaction(value):
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED]', value)

# Set up structlog processors to apply masking
def custom_logger(_, __, event_dict):
    if "credit_card" in event_dict:
        event_dict["credit_card"] = mask_credit_card(event_dict["credit_card"])
    if "ssn" in event_dict:
        event_dict["ssn"] = redact_ssn(event_dict["ssn"])
    if "email" in event_dict:
        event_dict["email"] = email_redaction(event_dict["email"])
    return event_dict

structlog.configure(
    processors=[
        custom_logger,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()
log.info("User registration", credit_card="1234567812345678", ssn="123-45-6789", email="user@example.com")

# It will generate like this
# {
#   "event": "User registration",
#   "credit_card": "1234********5678",
#   "ssn": "***-**-****",
#   "email": "[REDACTED]"
# }
