"""
Pydantic-related Helpers
"""

from __future__ import annotations

import mimetypes
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    ValidationError,
)
from typing import (
    Annotated,
    Any,
    Callable,
)

from .printing import print_ind


# -----------------------------------------------------------------------------------------
# TYPES

type NE_str      = Annotated[ str, Field( pattern = r"^[^\s].+$")]
""" Non-empty string (at least 2 chars and first char cannot be whitespace) """

type NE_var_name = Annotated[ str, Field( pattern = r"^[A-Za-z\_]\w+$")]
""" Non-empty variable name (at least 2 chars) """

type NumericID   = Annotated[ str, Field( pattern = r"^[0-9]+$")]
""" Numeric ID """

type SHA256_Hex  = Annotated[ str, Field( pattern = r"^[A-Fa-f0-9]{64}$")]
""" SHA-256 hash in hexadecimal format """

type UnixTS      = Annotated[ str, Field( pattern = r"^[1-9][0-9]*$")]
""" Unix timestamp """


# Add MIME types used by WhatsApp that `python:3.12-slim` does not include
mimetypes.add_type( "audio/ogg",  ".ogg" )
mimetypes.add_type( "image/webp", ".webp")

def validate_mime_type( value : str) -> str :
    """
    Validate MIME type
    Args:
        value : MIME type
    Returns:
        Cleaned MIME type string (lowercase, stripped, codec removed)
    Raises:
        ValueError : If MIME type is invalid
    """
    if (
        isinstance( value, str)
        and
        (
            cleaned_value := (
                value.lower().strip().split( ";", maxsplit = 1)[0].strip()
            )
        )
        and
        mimetypes.guess_extension(cleaned_value)
    ) :
        return cleaned_value
    
    raise ValueError(f"MIME type '{value}' is invalid")

type MIME_Type = Annotated[ str, AfterValidator(validate_mime_type)]
""" MIME Type """


# -----------------------------------------------------------------------------------------
# FUNCTIONS

def print_validation_errors( ve : ValidationError, indent : int = 1) -> None :
    """
    Pretty-print pydantic validation errors with indentation \\
    Args:
        validation_error : ValidationError object raised by pydantic
        indent           : Indentation level when printing
    """
    
    for error in ve.errors() :
        
        location_raw = error.get( "loc", ())
        if location_raw :
            location = str(" -> ").join( str(part) for part in location_raw )
        else :
            location = "<root>"
        
        message = error.get( "msg", "Validation error")
        
        print_ind( f"Location : {location}", indent)
        print_ind( f"Message  : {message}",  indent)
    
    return


def serialize_without_nones(
    basemodel : BaseModel,
    handler   : Callable[ [BaseModel], dict[ str, Any]],
) -> dict[ str, Any] :
    
    return {
        key : val for (key,val) in handler(basemodel).items() if val is not None
    }
