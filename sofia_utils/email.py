from __future__ import annotations

import httpx
import os
import requests

from pathlib import Path

from .class_wrappers import SafeWarningDict
from .printing import get_qualname as here


type Attachment = tuple[ str, bytes, str]


def render_template(
    path   : Path,
    params : dict[ str, object],
) -> str :
    
    template    = path.read_text( encoding = "utf-8")
    safe_params = SafeWarningDict(params)
    
    return template.format_map(safe_params)


def send_via_mailgun(
    *,
    api_key_name   : str = "MG_API_KEY",
    mailgun_domain : str,
    sender_name    : str | None = None,
    from_email     : str,
    to_email       : str,
    cc_to          : str | None = None,
    bcc_to         : str | None = None,
    subject        : str,
    html_body      : str,
    text_body      : str | None = None,
    attachments    : list[Attachment] | None = None,
    timeout        : int = 45,
) -> None :
    """
    Send an email through Mailgun synchronously.
    """
    
    if not ( mailgun_api_key := os.getenv(api_key_name) ) :
        raise RuntimeError(
            f"In {here()}: Mailgun API key env var '{api_key_name}' was not found"
        )
    if not mailgun_domain :
        raise ValueError(
            f"In {here()}: Mailgun email field 'mailgun_domain' must not be empty"
        )
    if not from_email :
        raise ValueError(
            f"In {here()}: Mailgun email field 'from_email' must not be empty"
        )
    
    payload = {
        "from"    : (
            f"{sender_name} <{from_email}>"
            if sender_name else
            from_email
        ),
        "to"      : to_email,
        "subject" : subject,
        "html"    : html_body,
    }
    
    if cc_to :
        payload["cc"] = cc_to
    
    if bcc_to :
        payload["bcc"] = bcc_to
    
    if text_body is not None :
        payload["text"] = text_body
    
    files_payload = [
        ( "attachment", ( filename, content, mime_type ) )
        for filename, content, mime_type in ( attachments or [] )
    ]
    
    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth    = ( "api", mailgun_api_key ),
        data    = payload,
        files   = files_payload or None,
        timeout = timeout,
    )
    
    try :
        response.raise_for_status()
    
    except requests.HTTPError as ex :
        raise RuntimeError(
            f"In {here()}: Mailgun error ({response.status_code}): {response.text}"
        ) from ex
    
    return


async def async_send_via_mailgun(
    *,
    api_key_name   : str = "MG_API_KEY",
    mailgun_domain : str,
    sender_name    : str | None = None,
    from_email     : str,
    to_email       : str,
    cc_to          : str | None = None,
    bcc_to         : str | None = None,
    subject        : str,
    html_body      : str,
    text_body      : str | None = None,
    attachments    : list[Attachment] | None = None,
    timeout        : int = 45,
) -> None :
    """
    Send an email through Mailgun asynchronously.
    """
    if not ( mailgun_api_key := os.getenv(api_key_name) ) :
        raise RuntimeError(
            f"In {here()}: Mailgun API key env var '{api_key_name}' was not found"
        )
    if not mailgun_domain :
        raise ValueError(
            f"In {here()}: Mailgun email field 'mailgun_domain' must not be empty"
        )
    if not from_email :
        raise ValueError(
            f"In {here()}: Mailgun email field 'from_email' must not be empty"
        )
    
    payload = {
        "from"    : (
            f"{sender_name} <{from_email}>"
            if sender_name else
            from_email
        ),
        "to"      : to_email,
        "subject" : subject,
        "html"    : html_body,
    }
    
    if cc_to :
        payload["cc"] = cc_to
    
    if bcc_to :
        payload["bcc"] = bcc_to
    
    if text_body is not None :
        payload["text"] = text_body
    
    files_payload = [
        ( "attachment", ( filename, content, mime_type ) )
        for filename, content, mime_type in ( attachments or [] )
    ]
    
    async with httpx.AsyncClient( timeout = timeout) as client :
        response = await client.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth  = ( "api", mailgun_api_key ),
            data  = payload,
            files = files_payload or None,
        )
    
    try :
        response.raise_for_status()
    
    except httpx.HTTPStatusError as ex :
        raise RuntimeError(
            f"In {here()}: Mailgun error ({response.status_code}): {response.text}"
        ) from ex
    
    return
