#!/usr/bin/env python3
"""
Utilities for file input/output (IO). Mostly wrappers of pathlib.
"""

import json
from base64 import b64encode
from collections import OrderedDict
from enum import Enum
from glob import glob
from pathlib import Path
from typing import Any


JSON_INDENT = 4
""" Default JSON Indentation Level """

class LoadMode(Enum) :
    """
    Loading Mode: GROUP | MERGE
    """
    GROUP = "group"
    MERGE = "merge"


def clean_filename( filename         : str | Path,
                    remove_prefix    : bool = True,
                    remove_extension : bool = True ) -> str :
    """
    Clean filename by removing prefix and/or extension \\
    Args:
        remove_prefix    : Whether to remove the filename's first prefix
        remove_extension : Whether to remove the filename's extension
    Returns:
        Filename with prefix and/or extension removed
    """
    fname_str = Path(filename).name
    if ( "_" in fname_str ) and remove_prefix :
        fname_str = "_".join( fname_str.split("_")[1:] )
    if ( "." in fname_str ) and remove_extension :
        fname_str = "".join( fname_str.split(".")[:1] )
    
    return fname_str

def encode_image( image_path : str | Path) -> str | None :
    """
    Encode an image to base64 \\
    Args:
        image_path : Image name or path
    Returns:
        * If image found: String containing the image's base64 encoding
        * If image not found: None
    """
    try :
        image_bytes = Path(image_path).read_bytes()
        return b64encode(image_bytes).decode('utf-8')
    
    except FileNotFoundError :
        print(f"❌ Error: File {image_path} not found")
    except Exception as ex :
        print(f"❌ Error: {ex}")
    
    return None

def ensure_dir( dirpath : str | Path) -> None :
    """
    Ensure directory exists \\
    Args:
        dirpath : Directory name or path
    """
    Path(dirpath).mkdir( parents = True, exist_ok = True)
    return

def exists_file( filepath : str | Path) -> bool :
    """
    Check if a file exists \\
    Args:
        filepath : File name or path
    Returns:
        True if file path exists, False otherwise.
    """
    return Path(filepath).exists()

def extract_code_block( data : str) -> str :
    """
    Extract content within first code block in string. If no code block found, fall back to assuming entire string is code. \\
    Args:
        data: Input string
    Returns:
        Output string
    """
    data  = data.strip()
    lines = data.split('\n')
    
    found_code_block  = False
    inside_code_block = False
    result_lines      = []
    
    for line in lines :
        stripped_line = line.strip()
        # Check if we're entering a code block
        if stripped_line.startswith('```') :
            # If we already found and completed a code block, stop processing
            if found_code_block and not inside_code_block :
                break
            # Check if it's a format-specific code block (e.g., ```json)
            if len(stripped_line) > 3 :
                inside_code_block = True
                found_code_block  = True
            else :
                # No format specification, toggle state
                inside_code_block = not inside_code_block
                if inside_code_block :
                    found_code_block = True
            continue
        # If we're in a code block, add the line
        if inside_code_block :
            result_lines.append(line)
    
    # If no code blocks were found, assume the entire string is code
    if not found_code_block :
        return data
    
    return '\n'.join(result_lines)

def list_files_starting_with( directory  : str | Path,
                              prefix     : str,
                              extensions : str | list[str] | tuple[str] ) -> list[str] :
    """
    List files in a directory starting with a given prefix and extension(s). \\
    Args:
        directory  : Directory name or path
        prefix     : Target file prefix
        extensions : Target file extension(s)
    Returns:
        Sorted list of filepaths (alphabetical order)
    """
    if isinstance( extensions, str) :
        ext_candidates = [ extensions ]
        if extensions == 'json' :
            ext_candidates.append('jsonc')
    
    elif isinstance( extensions, list) or isinstance( extensions, tuple) :
        ext_candidates = set(extensions)
    
    else :
        msg = f"Invalid 'extensions' type: {type(extensions)}"
        raise TypeError(f"In list_files_starting_with: {msg}")
    
    filepaths = []
    for ext in ext_candidates :
        filepaths.extend( glob(f'{str(directory)}/{prefix}*.{ext}') )
    
    return sorted(filepaths)

def load_file_as_binary( filepath : str | Path) -> bytes | None :
    """
    Load file as bytes object (binary data) \\
    Args:
        filepath: File name or path
    Returns:
        * If file found then bytes object
        * If file not found then None
    """
    try :
        return Path(filepath).read_bytes()
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    return

def load_file_as_string( filepath : str | Path) -> str | None :
    """
    Load file as string \\
    Args:
        filepath: File name or path
    Returns:
        * If file found then string
        * If file not found then None
    """
    try :
        return Path(filepath).read_text( encoding = "utf-8")
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    return

def load_json_file( filepath : str | Path) -> Any | None :
    """
    Deserialize JSON or JSONC file \\
    Args:
        filepath: File name or path
    Returns:
        * If file found then deserialized content
        * If file not found then None
    """
    filepath = Path(filepath)
    try :
        data = filepath.read_text( encoding = "utf-8")
        return load_json_string( data, filepath.suffix.lower() == '.jsonc')
    
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    
    return

def load_json_dicts_starting_with( directory : str | Path,
                                   prefix    : str,
                                   mode      : LoadMode
                                 ) -> OrderedDict :
    """
    Load all JSON/JSONC dict-type files in a directory starting with a given prefix \\
    Args:
        directory : Directory name or path
        prefix    : Target file prefix
        mode      : Loading mode (group or merge)
    Returns:
        Ordered dict depending on loading mode:
        * LoadMode.GROUP: Maps clean filenames to file contents
        * LoadMode.MERGE: Union of the contents of all files
    """
    result = OrderedDict()
    files  = list_files_starting_with( directory, prefix, "json")
    
    for file_path in files :
        data : OrderedDict = load_json_file(file_path)
        match mode :
            case LoadMode.GROUP :
                clean_fn         = clean_filename( file_path, True, True)
                result[clean_fn] = data
            case LoadMode.MERGE :
                result.update(data)
    
    return result

def load_json_lists_starting_with( directory : str | Path,
                                   prefix    : str,
                                   mode      : LoadMode
                                 ) -> list[Any] | OrderedDict[ str: Any] :
    """
    Load all JSON list-type files in a directory starting with a given prefix \\
    Args:
        directory : Directory name or path
        prefix    : Target file prefix
        mode      : Loading mode (group or merge)
    Returns:
        * LoadMode.GROUP: Ordered dict mapping clean filenames to file contents
        * LoadMode.MERGE: Single list with the combined contents of all files
    """
    result = None
    match mode :
        case LoadMode.GROUP :
            result = OrderedDict()
        case LoadMode.MERGE :
            result = []
    
    files = list_files_starting_with( directory, prefix, "json")
    for file_path in files :
        data : OrderedDict = load_json_file(file_path)
        match mode :
            case LoadMode.GROUP :
                clean_fn         = clean_filename( file_path, True, True)
                result[clean_fn] = data
            case LoadMode.MERGE :
                result.extend(data)
    
    return result

def load_json_string( data : str, comments : bool = False ) -> Any :
    """
    Deserialize JSON/JSONC string \\
    Args:
        data     : JSON/JSONC string
        comments : Whether it is necessary to strip JSONC comments
    Returns:
        Deserialized content
    """
    if comments :
        data = strip_jsonc_comments(data)
    return json.loads( data, object_pairs_hook = OrderedDict)

def remove_indentation( data : str) -> str :
    """
    Remove indentation line-by-line \\
    Args:
        data : Input string
    Returns:
        String with no indentation at the beginning of each line
    """
    lines_all = data.split('\n')
    lines_new = []
    for line in lines_all :
        lines_new.append(line.lstrip())
    return '\n'.join(lines_new)

def strip_jsonc_comments( data : str) -> str :
    """
    Remove JSONC-style comments (both inline '//' and block '/* */') from string. \\
    Args:
        data : Input string
    Returns:
        JSON-compatible string (with no JSONC-style comments)
    """
    result                 = []
    in_string              = False
    in_single_line_comment = False
    in_multi_line_comment  = False
    index                  = 0
    length                 = len(data)
    
    while index < length :
        current_char = data[index]
        next_char    = data[index + 1] if index + 1 < length else ''
        
        if in_single_line_comment :
            if current_char in ( '\n', '\r') :
                in_single_line_comment = False
                result.append(current_char)
            index += 1
            continue
        
        if in_multi_line_comment :
            if current_char in ( '\n', '\r') :
                result.append(current_char)
            if current_char == '*' and next_char == '/' :
                in_multi_line_comment = False
                index += 2
            else :
                index += 1
            continue
        
        if current_char == '"' :
            result.append(current_char)
            backslash_count = 0
            pos             = index - 1
            while pos >= 0 and data[pos] == '\\' :
                backslash_count += 1
                pos             -= 1
            if backslash_count % 2 == 0 :
                in_string = not in_string
            index += 1
            continue
        
        if not in_string and current_char == '/' and next_char == '/' :
            in_single_line_comment = True
            index += 2
            continue
        
        if not in_string and current_char == '/' and next_char == '*' :
            in_multi_line_comment = True
            index += 2
            continue
        
        result.append(current_char)
        index += 1
    
    return ''.join(result)

def write_to_file( filepath : str | Path, data : str) -> int :
    """
    Write text data to file \\
    Args:
        filepath : Output file name or path
        data     : Text to write
    Returns:
        Number of characters written to file
    """
    return Path(filepath).write_text( data, encoding = "utf-8")

def write_to_json_file( filepath : str | Path,
                        data     : Any,
                        indent   : int | None = JSON_INDENT) -> int :
    """
    Serialize object as JSON file \\
    Args:
        filepath : Output file name or path
        data     : Object to serialize
        indent   : Number of indentation spaces
    Returns:
        Number of characters written to file
    """
    data_str = write_to_json_string( data, indent)
    
    return Path(filepath).write_text( data_str, encoding = "utf-8")

def write_to_json_string( data : Any, indent : int | None = JSON_INDENT) -> str :
    """
    Serialize object as JSON string \\
    Args:
        data   : Object to serialize
        indent : Number of indentation spaces
    Returns:
        JSON-compatible string
    """
    return json.dumps( data,
                       ensure_ascii = False,
                       indent       = indent,
                       separators   = (",",":") if indent is None else None )
