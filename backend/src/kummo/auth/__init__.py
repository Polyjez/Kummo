"""Authentication: Supabase Auth behind a transparent /api/auth surface.

Layering, outermost first:

    api/auth.py    HTTP routes; knows cookies and status codes
    dependencies   guards for authenticated routes
    profiles       links a verified identity to kummo.clients / kummo.vendors
    cookies        session transport (HttpOnly, never readable by page JS)
    tokens         access-token verification
    service        the only module aware that the provider is Supabase
"""
