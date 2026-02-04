#!/usr/bin/env python3
"""
Utilities for counting tokens
"""

from pathlib import Path
from sys import argv
from tiktoken import encoding_for_model

from .io import ( load_file_as_string,
                  load_json_string,
                  write_to_json_string )
from .printing import print_sep


NO_INDENT_FLAG = "indent=None"


def count_tokens_in_string( model_name : str,
                            input_str  : str) -> int | None :
    """
    Returns the number of tokens in a text string \\
    Args:
        `model_name` : Tokenizer model name (e.g., 'gpt-4-mini')
        `input_str`  : Input string
    Returns
        If encoding succeeds then number of tokens in string; else None.
    """
    try :
        encoding = encoding_for_model(model_name)
        return len(encoding.encode(input_str))
    
    except KeyError as ke :
        print(f"Tiktoken does not recognize model name '{model_name}'")
        print(f"Exception data: {ke}")
    
    return None


def count_tokens_in_files( model_name : str,
                           directory  : str | Path,
                           extensions : tuple[ str, ...] = ( '.json', '.md')
                         ) -> dict[ str , str] :
    """
    Produce token counts for all JSON and Markdown files in the given directory \\
    Args:
        `model_name` : Tokenizer model name (e.g., 'gpt-4-mini')
        `directory`  : Target directory
        `extensions` : Optional; file extensions to process.
    Returns:
        Dictionary with filenames as keys and token counts as values
    """
    
    tokens = {}
    
    # Ensure model name is recognized
    if count_tokens_in_string( model_name, "hello") :
        
        dir_path = Path(directory)
        
        dir_files : list[Path] = []
        for ext in extensions :
            dir_files.extend( list( dir_path.glob(f"*{ext}") ) )
        
        for file in dir_files :
            
            file_str = load_file_as_string(file)
            if file_str :
                tokens[file.name] = count_tokens_in_string( model_name, file_str)
                
                if file.suffix == ".json" :
                    data            = load_json_string(file_str)
                    ni_file         = f"{file.stem}_{NO_INDENT_FLAG}.json"
                    ni_file_str     = write_to_json_string( data, indent = None)
                    tokens[ni_file] = count_tokens_in_string( model_name, ni_file_str)
    
    return tokens


if __name__ == "__main__" :
    
    package_name = Path(__file__).parent.name
    module_name  = Path(__file__).stem
    
    usage = f"Usage: python3 -m {package_name}.{module_name} <directory>"
    if len(argv) not in ( 2, 3) :
        raise SystemExit(usage)
    
    model_name = argv[1]
    if model_name in ( "-h", "--help") :
        raise SystemExit(usage)
    
    dir_str  = argv[2] if len(argv) == 3 else "."
    dir_path = Path(dir_str).expanduser().resolve()
    
    if dir_path.exists() and dir_path.is_dir() :
        
        tokens = count_tokens_in_files( model_name, dir_path)
        
        print_sep()
        print("Token counts per file:")
        print_sep()
        
        total_tokens = 0
        for filename, count in sorted(tokens.items()) :
            print(f"{filename:<70}{count:>10}")
            total_tokens += count if ( NO_INDENT_FLAG not in filename ) else 0
        
        print_sep()
        
        msg = "Total tokens across all files:"
        print(f"{msg:<70}{total_tokens:>10}")
        print(f"(Excluding '{NO_INDENT_FLAG}')")
        print_sep()
