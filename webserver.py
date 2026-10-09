from commands import StartCountdownCommand, CancelCountdownCommand, PlayTrainNowCommand

INDEX_FILE = "index.html"


class WebServerController:
    """WebServerController wraps adafruit_httpserver and enqueues commands from HTTP requests.
    
    Can be used with dependency injection for server/socketpool or test mocks.
    """
    def __init__(self, server=None, logger=None, index_path=INDEX_FILE, mdns_server=None):
        self._server = server
        self._logger = logger
        self._index_path = index_path
        self._mdns_server = mdns_server
        self._pending_commands = []

        if self._server is not None:
            # Set default headers to avoid keep-alive socket contention on microcontrollers
            self._server.headers = {
                "Connection": "close",
                "Access-Control-Allow-Origin": "*",
            }
            self._setup_routes()

    def _setup_routes(self):
        from adafruit_httpserver import GET, POST, Request, Response

        server = self._server

        @server.route("/", GET)
        def index_handler(request: Request):
            try:
                with open(self._index_path, "r") as f:
                    html_content = f.read()
                # Set Cache-Control to allow clients to cache index.html for 24 hours (86400s).
                # Microcontroller performance benefit: Avoids handling repeated HTTP requests
                # and socket connections entirely on subsequent visits.
                # Tradeoff: If index.html is modified, browser users must hard-refresh (Ctrl+F5)
                # or clear browser cache to see UI updates immediately.
                return Response(
                    request,
                    html_content,
                    content_type="text/html",
                    headers={"Cache-Control": "public, max-age=86400"},
                )
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Failed to read {self._index_path}: {e}")
                return Response(request, "Error loading index.html", content_type="text/plain")

        @server.route("/favicon.ico", GET)
        def favicon_handler(request: Request):
            # Return empty response for browsers requesting favicon to avoid hanging retries
            return Response(request, "", content_type="image/x-icon")

        @server.route("/api/v1/timer", POST)
        def timer_handler(request: Request):
            # Parse query params (e.g. /api/v1/timer?seconds=300)
            seconds = 300
            if "seconds" in request.query_params:
                try:
                    seconds = int(request.query_params.get("seconds"))
                except (ValueError, TypeError):
                    seconds = 300
            
            if self._logger:
                self._logger.info(f"webserver: start countdown {seconds}s")
            self._pending_commands.append(StartCountdownCommand(seconds))
            return Response(request, f"Started {seconds}s countdown", content_type="text/plain")

        @server.route("/api/v1/train", POST)
        def train_handler(request: Request):
            if self._logger:
                self._logger.info("webserver: play train now")
            self._pending_commands.append(PlayTrainNowCommand())
            return Response(request, "Playing train", content_type="text/plain")

        @server.route("/api/v1/cancel", POST)
        def cancel_handler(request: Request):
            if self._logger:
                self._logger.info("webserver: cancel countdown")
            self._pending_commands.append(CancelCountdownCommand())
            return Response(request, "Countdown cancelled", content_type="text/plain")

    def enqueue_command(self, command):
        """Allows test fixtures or local callers to enqueue a command directly."""
        self._pending_commands.append(command)

    def poll(self) -> list:
        if self._server is not None:
            try:
                self._server.poll()
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Error in webserver.poll(): {e}")

        commands = self._pending_commands
        self._pending_commands = []
        return commands


def create_webserver_controller(pool, radio, logger=None, port=80, hostname="train"):
    """Creates and starts the WebServerController with mDNS service."""
    import mdns
    from adafruit_httpserver import Server

    # 1. Setup mDNS (e.g. http://train.local)
    mdns_server = None
    try:
        mdns_server = mdns.Server(radio)
        mdns_server.hostname = hostname
        mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=port)
        if logger:
            logger.info(f"mDNS advertised as {hostname}.local")
    except Exception as e:
        if logger:
            logger.error(f"Failed to setup mDNS: {e}")

    # 2. Setup HTTP server
    server = Server(pool, debug=False)
    # Retain mdns_server in WebServerController so it is never garbage collected
    controller = WebServerController(server=server, logger=logger, mdns_server=mdns_server)
    
    server.start(str(radio.ipv4_address), port=port)
    if logger:
        logger.info(f"Web server started at http://{radio.ipv4_address}:{port}")

    return controller
