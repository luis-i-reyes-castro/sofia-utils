"""
Utilities for generating stamps (UUIDs, timestamps, sha256, etc.)
"""

from __future__ import annotations

from datetime import ( datetime,
                       timezone,
                       timedelta )
from hashlib import sha256
from random import ( choices,
                     randrange )
from string import ascii_letters
from string import digits
from uuid import uuid4


def generate_B62ID( length : int) -> str :
    """
    Generate random Base62 ID \\
    Args:
        length: Desired number of characters
    Returns:
        Random string of ASCII letters and digits
    """
    return "".join( choices( list( ascii_letters + digits ), k = length) )

def generate_number( length : int) -> str :
    """
    Generate a random sequence of digits \\
    Args:
        length: Desired number of digits
    Returns:
        Random sequence of digits (including, possibly, leading zeros).
    """
    return "".join( choices( list(digits), k = length) )

def generate_rand_date( start_date : str | None = None,
                        end_date   : str | None = None ) -> str:
    """
    Generate a random date between start_date and end_date \\
    Args:
        start_date : 'DD/MM/YYYY' or None. If None then use today's date one year ago.
        end_date   : 'DD/MM/YYYY' or None. If None then use today's date.
    Returns:
        str: Random date in interval (endpoints inclusive) in 'DD/MM/YYYY' format.
    """
    
    if start_date :
        start_time = datetime.strptime( start_date, "%d/%m/%Y")
    else :
        start_time = datetime.now() - timedelta( days = 365)
    
    if end_date :
        end_time = datetime.strptime( end_date, "%d/%m/%Y")
    else :
        end_time = datetime.now()
    
    if start_time > end_time :
        msg = "Start date is later than end date\n" \
            + f"Start date: {start_time.strftime('%d/%m/%Y')}\n" \
            + f"End date  : {end_time.strftime('%d/%m/%Y')}"
        raise ValueError(f"In generate_rand_date: {msg}")
    
    elif start_time == end_time :
        return start_time.strftime("%d/%m/%Y")
    
    time_between = end_time - start_time
    random_days  = randrange(time_between.days + 1)
    random_date  = start_time + timedelta( days = random_days)
    
    return random_date.strftime("%d/%m/%Y")

def generate_UUID() -> str :
    """
    Generate a standard UUID-4. This is a random Universal Unique Identifier (UUID) composed of 32 hexadecimal digits (128 bits) grouped as 8-4-4-4-12, separated by hyphens, for a total of 36 characters. \\
    Returns:
        'xxxxxxxx-xxxx-4xxx-Nxxx-xxxxxxxxxxxx' where N in ( 8, 9, a, b)
    """
    return str(uuid4())

def get_now_utc_iso() -> str :
    """
    Get current UTC time as ISO 8601 formatted string \\
    Returns:
        ISO 8601 UTC timestamp including microseconds and Z suffix.
        E.g., "2024-01-15T10:32:58.125098Z".
    """
    
    now_dt  = datetime.now(timezone.utc)
    now_str = now_dt.isoformat( timespec = "microseconds")
    now_str = now_str.replace( "+00:00", "Z")
    
    return now_str

def get_sha256( data : bytes) -> str :
    """
    Calculate SHA-256 hash of bytes object \\
    Args:
        data : object to hash
    Returns:
        SHA-256 hash of the object's binary content
    """
    h = sha256()
    h.update(data)
    return h.hexdigest()

def unix_to_utc_iso( epoch : int | float | str | None) -> str | None :
    """
    Convert a Unix epoch timestamp to ISO 8601 formatted string \\
    Args:
        epoch : Unix epoch timestamp (seconds since 1970-01-01T00:00:00) or None
    Returns:
        If conversion succeeded then ISO 8601 UTC timestamp including seconds and Z suffix,
        e.g., "2024-01-15T10:32:58Z"; else None.
    """
    if epoch :
        try :
            ts_dt  = datetime.fromtimestamp( float(epoch), tz = timezone.utc)
            ts_str = ts_dt.isoformat( timespec = "seconds")
            ts_str = ts_str.replace( "+00:00", "Z")
            return ts_str
        
        except Exception as ex :
            print(f"In unix_to_utc_iso: {ex}")
    
    return None

def utc_iso_to_dt( timestamp : str | None) -> datetime | None :
    """
    Convert ISO 8601 timestamp string to datetime object. \\
    Handles both formats with and without 'Z' suffix for UTC timezone. \\
    Args:
        timestamp : ISO 8601 timestamp string or None
    Returns:
        If conversion succeeded then datetime object; else None.
    """
    if timestamp :
        try :
            if timestamp.endswith("Z") :
                timestamp = timestamp.replace( "Z", "+00:00")
            return datetime.fromisoformat(timestamp)
        
        except Exception as ex :
            print(f"In utc_iso_to_dt: {ex}")
    
    return None
