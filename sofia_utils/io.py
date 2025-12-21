#!/usr/bin/env python3
"""
Utilities for file input/output (IO)
"""

import json
from base64 import b64encode
from collections import OrderedDict
from enum import Enum
from glob import glob
from pathlib import Path
from typing import Any

""" Default JSON Indentation Level """
JSON_INDENT = 4

class LoadMode(Enum) :
    GROUP = "group"
    MERGE = "merge"

def clean_filename( filename         : str | Path,
                    remove_prefix    : bool = True,
                    remove_extension : bool = True ) -> str :
    
    new_fname = Path(filename).name
    if remove_prefix :
        new_fname = "_".join( new_fname.split("_")[1:] )
    if remove_extension :
        new_fname = "".join( new_fname.split(".")[:1] )
    
    return new_fname

def encode_image( image_path : str | Path) -> str | None :
    """Encode the image to base64."""
    try:
        with open( image_path, "rb") as image_file:
            return b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ Error: File {image_path} not found")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def ensure_dir( dir_name : str | Path) -> None :
    """
    Ensure directory exists.
    """
    Path(dir_name).mkdir( parents = True, exist_ok = True)
    return

def exists_file( filepath : str | Path) -> bool :
    """
    Check if a file exists.
    """
    return Path(filepath).exists()

def extract_code_block( data : str) -> str :
    """
    Extract content within first code block in string. If no code block found, fall back to assuming entire string is code.
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

def list_files_starting_with( directory : str | Path,
                              prefix : str,
                              extensions : str | list[str] | tuple[str] ) -> list[str] :
    """
    List files in a directory starting with a given prefix and extension(s).
    """
    if isinstance( extensions, str) :
        ext_candidates = [ extensions ]
        if extensions == 'json' :
            ext_candidates.append('jsonc')
    
    elif isinstance( extensions, list) or isinstance( extensions, tuple) :
        ext_candidates = list( set(extensions) )
    
    else :
        msg = f"Invalid 'extensions' type: {type(extensions)}"
        raise TypeError(f"In list_files_starting_with: {msg}")
    
    filepaths = []
    for ext in ext_candidates :
        filepaths.extend( glob(f'{str(directory)}/{prefix}*.{ext}') )
    
    return sorted(filepaths)

def load_file_as_binary( filepath : str | Path) -> bytes | None :
    """
    Load file as binary data
    """
    try :
        with open( filepath, "rb") as file :
            return file.read()
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    return

def load_file_as_string( filepath : str | Path) -> str | None :
    """
    Load any file as string
    """
    try :
        with open( filepath, 'r', encoding = 'utf-8') as f :
            return f.read()
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    return

def load_json_file( filepath : str | Path) -> Any | None :
    """
    Load JSON file data
    """
    filepath = Path(filepath)
    try :
        with open( filepath, 'r', encoding = 'utf-8') as f :
            data = f.read()
        if filepath.suffix == '.jsonc' :
            data = strip_jsonc_comments(data)
        return json.loads( data, object_pairs_hook = OrderedDict)
    
    except FileNotFoundError :
        print(f"❌ Error: File {filepath} not found")
    
    return

def load_json_dicts_starting_with( directory : str | Path,
                                   prefix    : str,
                                   mode      : LoadMode
                                 ) -> OrderedDict :
    """
    Load all JSON dict-type files in a directory starting with a given prefix
    and combine them or group them into one OrderedDict.
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
    Load all JSON list-type files in a directory starting with a given prefix
    and combine them into one list or group them into one OrderedDict.
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
    Load JSON from a string, handling markdown code blocks if present.
    """
    if comments :
        data = strip_jsonc_comments(data)
    return json.loads( data, object_pairs_hook = OrderedDict)

def remove_indentation( data : str) -> str :
    """
    Remove indentation line-by-line
    """
    lines_all = data.split('\n')
    lines_new = []
    for line in lines_all :
        lines_new.append(line.strip())
    return '\n'.join(lines_new)

def strip_jsonc_comments( data : str) -> str :
    """
    Remove JSONC-style comments (both inline '//' and block '/* */') from text.
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

def write_to_file( filepath : str | Path, data : str) -> None :
    """
    Write data to file
    """
    with open( filepath, 'w', encoding = 'utf-8') as f :
        f.write(data)
    return

def write_to_json_file( filepath : str | Path,
                        data     : Any,
                        indent   : int | None = JSON_INDENT) -> None :
    """
    Write data to JSON file
    """
    with open( filepath, 'w', encoding = 'utf-8') as f :
        json.dump( data, f, indent = indent, ensure_ascii = False)
    return

def write_to_json_string( data : Any, indent : int | None = JSON_INDENT) -> str :
    """
    Write data to JSON string
    """
    return json.dumps( data,
                       ensure_ascii = False,
                       indent       = indent,
                       separators   = (",",":") if indent is None else None )
