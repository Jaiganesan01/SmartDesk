# Wrapper to redirect extraction calls to the main ticket_extractor module
from ticket_extractor import extract_ticket_info, get_mock_extraction

__all__ = ["extract_ticket_info", "get_mock_extraction"]
