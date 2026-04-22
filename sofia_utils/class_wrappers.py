from __future__ import annotations

from typing import Final


__MISSING_OBJ__ : Final[object] = object()


class SafeWarningDict(dict) :
    """
    Dict with methods `get` and `__missing__` overloaded to print and return safe warnings.
    """
    
    def get( self, key : str, default : object = __MISSING_OBJ__) -> object :
        
        if key in self :
            return self[key]
        
        if default is not __MISSING_OBJ__ :
            return default
        
        return self.__missing__(key)
    
    def __missing__( self, key : str) -> str :
        
        print(f"WARNING: In SafeWarningDict: Key '{key}' is missing a value.")
        
        return f"__MISSING_KEY:{key}__"
