from fastapi import FastAPI, Response
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import asyncio

app = FastAPI()

# Métricas
REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
HEALTHCHECK_REQUESTS = Counter('healthcheck_requests_total', 'Total number of requests to healthcheck')
MAIN_ENDPOINT_REQUESTS = Counter('main_requests_total', 'Total number of requests to main endpoint')
BYE_ENDPOINT_REQUESTS = Counter('bye_requests_total', 'Total number of requests to bye endpoint')



class SimpleServer:
    """
    SimpleServer class define FastAPI configuration and implemented endpoints
    """

    _hypercorn_config = None

    def __init__(self):
        self._hypercorn_config = HyperCornConfig()

    async def run_server(self):
        """Starts the server with the config parameters"""
        self._hypercorn_config.bind = ['0.0.0.0:8081']
        self._hypercorn_config.keep_alive_timeout = 90
        await serve(app, self._hypercorn_config)

    @app.get("/health")
    async def health_check():
        """Implement health check endpoint"""
        REQUESTS.inc()
        HEALTHCHECK_REQUESTS.inc()
        return {"health": "ok"}

    @app.get("/")
    async def read_main():
        """Implement main endpoint"""
        REQUESTS.inc()
        MAIN_ENDPOINT_REQUESTS.inc()
        return {"msg": "Hello World"}

@app.get("/bye")
async def read_path(msg: str):
    """Implement bye endpoint"""
    REQUESTS.inc()
    BYE_ENDPOINT_REQUESTS.inc()
    return {"message": "Bye, Bye!", "input": msg}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Ejecutar el servidor en un loop asíncrono
if __name__ == "__main__":
    server = SimpleServer()
    asyncio.run(server.run_server())
