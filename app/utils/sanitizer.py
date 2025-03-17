from typing import Any, Dict, List, Optional, Union
from nh3 import clean as nh3_clean

def sanitize_string(value: Optional[str]) -> Optional[str]:
    """Sanitize a string using NH3 to prevent XSS attacks"""
    if value is None:
        return None
    return nh3_clean(value)

def sanitize_dict(data: Dict[str, Any], fields_to_sanitize: List[str]) -> Dict[str, Any]:
    """Sanitize specific string fields in a dictionary"""
    sanitized_data = data.copy()
    for field in fields_to_sanitize:
        if field in sanitized_data and isinstance(sanitized_data[field], str):
            sanitized_data[field] = sanitize_string(sanitized_data[field])
    return sanitized_data

def sanitize_list_of_dicts(
    data_list: List[Dict[str, Any]], 
    fields_to_sanitize: List[str]
) -> List[Dict[str, Any]]:
    """Sanitize specific string fields in a list of dictionaries"""
    return [sanitize_dict(item, fields_to_sanitize) for item in data_list]