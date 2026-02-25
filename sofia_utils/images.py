#!/usr/bin/env python3
"""
Utilities for image processing
"""

from io import BytesIO
from mimetypes import guess_type
from pathlib import Path

from PIL import Image, ImageOps


ALLOWED_EXTENSIONS = { ".jpg", ".jpeg", ".png" }


def resize_image( filename      : str,
                  image_bytes   : bytes,
                  size_limit_kb : int = 1024 ) -> bytes :
    """
    Resize image if needed to fit within size limit \\
    Args:
        filename      : File name with extension (.jpg, .jpeg, .png)
        image_bytes   : Image content as bytes
        size_limit_kb : Size limit in kilobytes (default 1024)
    Returns:
        Image bytes in the same MIME type
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS :
        ext_list = ", ".join(
            [ f"*{ext_item}" for ext_item in sorted(ALLOWED_EXTENSIONS) ]
        )
        e_msg = (
            "In resize_image: Unsupported filename extension. "
            f"Supported extensions are: {ext_list}"
        )
        raise ValueError(e_msg)
    
    mime_type   = guess_type(filename)[0]
    format_map  = { "image/jpeg" : "JPEG", "image/png" : "PNG" }
    format_name = format_map.get(mime_type)
    if not format_name :
        raise ValueError("In resize_image: Unsupported mime type")
    
    if not ( isinstance( image_bytes, bytes) and image_bytes ) :
        raise ValueError("In resize_image: No image bytes.")
    
    if not ( isinstance( size_limit_kb, int) and ( size_limit_kb > 0 ) ) :
        raise ValueError("In resize_image: size_limit_kb must be a positive int")
    
    limit_bytes = size_limit_kb * 1024
    
    if len(image_bytes) <= limit_bytes :
        return image_bytes
    
    try :
        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)
    except Exception as ex :
        raise ValueError("In resize_image: Invalid image bytes") from ex
    
    if ( format_name == "JPEG" ) and ( image.mode not in { "RGB", "L" } ) :
        image = image.convert("RGB")
    
    def encode_image( img       : Image.Image,
                      fmt_name  : str,
                      quality   : int | None = None ) -> bytes :
        
        buffer      = BytesIO()
        save_kwargs = { "format" : fmt_name }
        
        if fmt_name == "JPEG" :
            save_kwargs.update(
                { "quality"     : quality if quality is not None else 100,
                  "optimize"    : True,
                  "progressive" : True }
            )
        elif fmt_name == "PNG" :
            save_kwargs.update(
                { "optimize"       : True,
                  "compress_level" : 9 }
            )
        else :
            raise ValueError(f"In resize_image: Unsupported format '{fmt_name}'")
        
        img.save( buffer, **save_kwargs)
        return buffer.getvalue()
    
    current_image   = image
    max_iterations  = 12
    candidate_bytes = encode_image( current_image, format_name)
    
    for _ in range(max_iterations) :
        
        if len(candidate_bytes) <= limit_bytes :
            return candidate_bytes
        
        ratio      = ( limit_bytes / len(candidate_bytes) ) ** 0.8
        new_width  = max( 1, int( current_image.width  * ratio) )
        new_height = max( 1, int( current_image.height * ratio) )
        
        if ( new_width  == current_image.width  ) and \
           ( new_height == current_image.height ) :
            if ( current_image.width == 1 ) and ( current_image.height == 1 ) :
                return candidate_bytes
            new_width  = max( 1, current_image.width  - 1 )
            new_height = max( 1, current_image.height - 1 )
        
        new_dims        = ( new_width, new_height )
        current_image   = current_image.resize( new_dims, Image.LANCZOS)
        candidate_bytes = encode_image( current_image, format_name)
    
    return candidate_bytes
