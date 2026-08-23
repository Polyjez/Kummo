"""Reading the confirmation email out of the local mail catcher.

The local stack sends nothing: `[local_smtp]` in `supabase/config.toml` runs a mail
server that only collects. Its API is what makes the confirmation flow testable —
without it these tests would need the token hash, which exists nowhere else.
"""

import asyncio
import re

import httpx

# The web interface port from `[local_smtp]`; the API lives under the same origin.
MAIL_API = "http://127.0.0.1:54324/api/v1"

# What our own template puts in the link — see supabase/templates/confirmation.html.
TOKEN_HASH = re.compile(r"token_hash=([A-Za-z0-9_-]+)")


async def confirmation_token_hash(email: str, attempts: int = 40, delay: float = 0.25) -> str:
    """The token hash from the newest confirmation mail for `email`.

    Polled: the provider answers the sign-up before the message has been delivered, so
    the first look is usually too early.
    """
    async with httpx.AsyncClient(base_url=MAIL_API, timeout=5.0) as mail:
        for _ in range(attempts):
            found = await mail.get("/search", params={"query": f"to:{email}"})
            found.raise_for_status()
            for message in found.json().get("messages") or []:
                body = await mail.get(f"/message/{message['ID']}")
                match = TOKEN_HASH.search(body.text)
                if match:
                    return match.group(1)
            await asyncio.sleep(delay)

    raise AssertionError(f"No confirmation email arrived for {email}")
