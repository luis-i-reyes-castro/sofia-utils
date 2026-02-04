#!/usr/bin/env python3
"""
Utilities for printing and formatting string
"""

from re import match
from pydantic import ValidationError
from typing import Any


DEFAULT_INDENT = 'spaces'
""" Indentation default mode """
INDENT_SPACES = 4
""" Indentation spaces when in `spaces` mode """
MAX_RECURSION_DEPTH = 10
""" Maximum recursion depth for function `str_recursively` """
MIN_B64_IMG_ENCONDING_LENGTH = 2000
""" Minimum Base64 image encoding length. Strings of this length or longer will be suspected to being Base64 image encondings. """


def print_ind( argument     : str,
               indent_level : int = 0,
               indent_type  : str = DEFAULT_INDENT ) -> None :
    """
    Print indented string \\
    Args:
        argument     : Input string
        indent_level : Indentation level. Each level is `INDENT_SPACES` spaces or one tab.
        indent_type  : Indentation type: `spaces` | `tabs`
    """
    print(str_ind( argument, indent_level, indent_type))
    return

def print_recursively( data         : Any,
                       indent_level : int = 0,
                       indent_type  : str = DEFAULT_INDENT ) -> None :
    """
    Print string representation of object, recursively parsing contents. \\
    Args:
        data         : Input object
        indent_level : Indentation level. Each level is `INDENT_SPACES` spaces or one tab.
        indent_type  : Indentation type: `spaces` | `tabs`
    """
    print(str_recursively( data, indent_level, indent_type))
    return

def print_sep( width : int = 80) -> None :
    """
    Print separator string \\
    Args:
        width : Number of '-' characters in separator
    """
    print( '-' * width )
    return

def print_validation_errors( ve : ValidationError, indent : int = 4) -> None :
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

def str_ind( argument     : str,
             indent_level : int = 0,
             indent_type  : str = DEFAULT_INDENT ) -> str :
    """
    Indent string \\
    Args:
        argument     : Input string
        indent_level : Indentation level. Each level is `INDENT_SPACES` spaces or one tab.
        indent_type  : Indentation type: `spaces` | `tabs`
    Returns:
        Indented string
    """
    
    space = None
    match indent_type :
        case 'spaces' :
            space = ' ' * INDENT_SPACES * indent_level
        case 'tabs' :
            space = '\t' * indent_level
        case _ :
            raise ValueError(f"In str_ind: Invalid ind_type '{indent_type}'")
    
    lines  = str(argument).split('\n')
    result = []
    for line in lines :
        result.append(f'{space}{line}')
    
    return '\n'.join(result)

def str_recursively( data         : Any,
                     indent_level : int = 0,
                     indent_type  : str = DEFAULT_INDENT,
                     _visited     : set | None = None ) -> str :
    """
    Produce string representation of object, recursively parsing contents. \\
    Args:
        data         : Input object
        indent_level : Indentation level. Each level is `INDENT_SPACES` spaces or one tab.
        indent_type  : Indentation type: `spaces` | `tabs`
        _visited     : For internal use (leave as None)
    Returns:
        String representation of object
    """
    
    # Initialize visited set to track circular references
    if _visited is None :
        _visited = set()
    
    # Check for circular references
    data_id = id(data)
    if data_id in _visited :
        msg = f"<circular reference to {type(data).__name__}>"
        return str_ind( msg, indent_level, indent_type)
    
    # Add current object to visited set
    _visited.add(data_id)
    
    # None
    if data is None :
        _visited.remove(data_id)
        return str_ind( "None", indent_level, indent_type)
    
    # Raw binary data (bytes)
    elif isinstance( data, bytes):
        display_len = min( 4, len(data))
        shown       = data[:display_len]
        shown_str   = ' '.join( f'{b:02x}' for b in shown )
        
        if len(data) > 4 :
            shown_str += ' ...'
        
        _visited.remove(data_id)
        return str_ind( f"bytes: {shown_str}", indent_level, indent_type)
    
    # Strings
    elif isinstance( data, str) :

        # Check for Base64 image encoding
        if len(data) >= MIN_B64_IMG_ENCONDING_LENGTH :
            b64_chars = "A-Za-z0-9+/="
            if match( fr'data:image/[a-z]+;base64,[{b64_chars}]+$', data) \
            or match( fr'[{b64_chars}]+$', data) :
                _visited.remove(data_id)
                return str_ind( "str: [Base64 Image Enconding]", indent_level, indent_type)
        
        _visited.remove(data_id)
        return str_ind( f"str: {data}", indent_level, indent_type)
    
    # Numbers
    elif isinstance( data, int) or isinstance( data, float) :
        data_t = data.__class__.__name__
        _visited.remove(data_id)
        return str_ind( f"{data_t}: {str(data)}", indent_level, indent_type)
    
    # Lists and tuples
    elif isinstance( data, list) or isinstance( data, tuple) :
        
        title  = "list:" if isinstance( data, list) else "tuple:"
        border = '[]' if isinstance( data, list) else '()'
        
        if not data :
            _visited.remove(data_id)
            return str_ind( f"{title} {border}", indent_level, indent_type)
        
        result = []
        result.append( str_ind( title,     indent_level, indent_type) )
        result.append( str_ind( border[0], indent_level, indent_type) )
        
        for item in data :
            result.append( str_ind( '[>] item:',  indent_level,     indent_type) )
            result.append( str_recursively( item, indent_level + 1, indent_type, _visited) )
        
        result.append( str_ind( border[1], indent_level, indent_type) )
        
        _visited.remove(data_id)
        return '\n'.join(result)
    
    # Dictionaries
    elif isinstance( data, dict) :
        
        if not data :
            _visited.remove(data_id)
            return str_ind( "dict: {}", indent_level, indent_type)
        
        result = []
        result.append( str_ind( 'dict:', indent_level, indent_type) )
        result.append( str_ind( '{',     indent_level, indent_type) )
        
        for key, val in data.items() :
            result.append( str_ind( f'[>] {key}:',
                           indent_level,     indent_type) )
            result.append( str_recursively( val,
                           indent_level + 1, indent_type, _visited) )
        
        result.append( str_ind( '}', indent_level, indent_type) )
        
        _visited.remove(data_id)
        return '\n'.join(result)
    
    # Types
    elif isinstance( data, type) :
        _visited.remove(data_id)
        return str_ind( f"definition of class '{data.__name__}'", indent_level, indent_type)
    
    # Objects
    elif hasattr( data, "__class__") and hasattr( data.__class__, "__name__") :
        
        result  = []
        data_t  = data.__class__.__name__
        msg_str = f"object of class '{data_t}'"
        result.append( str_ind( msg_str, indent_level, indent_type) )

        # Prevent infinite recursion
        if indent_level > MAX_RECURSION_DEPTH :
            result.append( str_ind( f"<max depth reached>", indent_level + 1, indent_type) )
            _visited.remove(data_id)
            return '\n'.join(result)

        if hasattr( data, "__dict__") or hasattr( data, "__slots__") :
            
            attrs = {}
            if hasattr( data, "__dict__") :
                attrs = data.__dict__
            else :
                slots = getattr( data, "__slots__")
                if isinstance( slots, str) :
                    slots = [slots]
                for slot_ in slots :
                    if hasattr( data, slot_) :
                        attrs[slot_] = getattr( data, slot_)
            
            # Filter out internal/private attributes
            filtered_attrs = {}
            for att, val in attrs.items() :
                if not ( att.startswith( '_' ) or att.startswith( '__' ) ) :
                    filtered_attrs[att] = val
            
            if filtered_attrs :
                
                result.append( str_ind( '{', indent_level, indent_type) )
                
                for att, val in filtered_attrs.items() :
                    result.append( str_ind( f"[>] {att}:",
                                   indent_level,     indent_type) )
                    result.append( str_recursively( val,
                                   indent_level + 1, indent_type, _visited) )
                
                result.append( str_ind( '}', indent_level, indent_type) )
        
        _visited.remove(data_id)
        return '\n'.join(result)
    
    # Fallback
    _visited.remove(data_id)
    return str_ind( f"object of type {type(data)}", indent_level, indent_type)
