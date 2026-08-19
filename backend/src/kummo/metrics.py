"""Prometheus metrics, shared by every feature.

Two kinds of numbers live here. The HTTP ones are filled in by `main.py`'s
`request_context` middleware, which already measures every request — the metrics are
the same observation the log line makes, kept as a time series instead of a sentence.
The domain ones are incremented by the routes themselves, because "a sign-in failed"
is not visible from the status code alone once a route maps several errors onto 401.

Metric names are prefixed `kummo_` so they do not collide with the process and GC
collectors `prometheus_client` registers by default; those come along for free on the
same registry.

Labels are deliberately low cardinality: the *route template* (`/api/activities/{activity_id}`),
never the request path, or a series would be created per activity id. Everything served
by the static mount collapses to a single `static` label for the same reason.

One process, one registry: the app runs as a single uvicorn worker, so no multiprocess
mode is configured. Running several workers behind one port would need
`PROMETHEUS_MULTIPROC_DIR` and a `MultiProcessCollector`, otherwise each scrape hits
whichever worker answers and the counters look like they go backwards.
"""

from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

METRICS_PATH = "/metrics"

# The split the whole app is arranged around: everything under it is a route of ours,
# everything else is served by the static mount. `main.py` uses it to decide what to
# log; here it is what tells a 404 on a missing API route from one on a missing file.
API_PREFIX = "/api"

# The label used for anything the static mount served, and for a request that matched
# no route at all (a 404): both would otherwise be an unbounded set of paths.
STATIC_ENDPOINT = "static"
UNMATCHED_ENDPOINT = "unmatched"

http_requests_total = Counter(
    "kummo_http_requests_total",
    "HTTP requests handled, by route template and outcome",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "kummo_http_request_duration_seconds",
    "Time spent handling a request, in seconds",
    ["method", "endpoint"],
)

auth_events_total = Counter(
    "kummo_auth_events_total",
    "Authentication events, by kind and outcome",
    ["event", "outcome"],
)

activities_created_total = Counter(
    "kummo_activities_created_total",
    "Activities created by a vendor",
)

SUCCESS = "success"
FAILURE = "failure"

# The fixed set of `event` labels. Named here rather than spelled at each call site: a
# typo would silently open a second series instead of failing.
AUTH_REGISTER_CLIENT = "register_client"
AUTH_REGISTER_VENDOR = "register_vendor"
AUTH_LOGIN = "login"
AUTH_LOGOUT = "logout"
AUTH_REFRESH = "refresh"
AUTH_OAUTH_START = "oauth_start"
AUTH_OAUTH_CALLBACK = "oauth_callback"


def endpoint_of(request: Request) -> str:
    """The low-cardinality label for the route that handled this request.

    Read after the response is produced: the matched route is written into the scope
    while routing, so this is empty if called on the way in.

    The route only knows its own template (`/activities/{activity_id}`) — the `/api`
    that `include_router` put in front of it lives on the router above, not on the
    route — so the prefix is recovered from the request path, by stripping off the part
    the template accounts for. Anything that does not line up falls back to the bare
    template: a less precise label, never a wrong one.
    """
    path = request.url.path
    route = request.scope.get("route")
    if route is None:
        # No route matched. Under /api that is a 404 or a 405; anywhere else the static
        # mount answered, and those paths are unbounded.
        return UNMATCHED_ENDPOINT if path.startswith(API_PREFIX) else STATIC_ENDPOINT

    template = getattr(route, "path_format", None) or getattr(route, "path", "")
    try:
        matched = template.format(**(request.scope.get("path_params") or {}))
    except (KeyError, IndexError):
        return template
    # Case-insensitively, because a UUID may reach us in any case but reaches the
    # handler parsed and normalised.
    if matched and path.lower().endswith(matched.lower()):
        return path[: len(path) - len(matched)] + template
    return template


def record_request(request: Request, status_code: int, duration_seconds: float) -> None:
    """Record one handled request. Called once per request, from the middleware."""
    endpoint = endpoint_of(request)
    http_requests_total.labels(
        method=request.method, endpoint=endpoint, status=str(status_code)
    ).inc()
    http_request_duration_seconds.labels(
        method=request.method, endpoint=endpoint
    ).observe(duration_seconds)


def record_auth_event(event: str, outcome: str = SUCCESS) -> None:
    """Record an authentication event.

    `event` is a fixed identifier chosen at the call site — never anything the caller
    supplied, or a request could invent labels until the scrape falls over.
    """
    auth_events_total.labels(event=event, outcome=outcome).inc()


def record_activity_created() -> None:
    activities_created_total.inc()


# The scrape endpoint is one route with no model of its own — the Prometheus text
# format is the response body — so it lives here rather than in a package of its own.
router = APIRouter(tags=["metrics"])


@router.get(METRICS_PATH, include_in_schema=False)
async def scrape() -> Response:
    """The Prometheus scrape endpoint.

    Unauthenticated, and outside `/api` so the middleware does not log a line per
    scrape. It exposes counts and timings only — no identifiers, no user data — and is
    expected to be reachable only from inside the deployment's network boundary.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
