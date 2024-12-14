# # start a fastapi server with uvicorn



import uvicorn
from u_copilot.main import app
from u_copilot.settings.settings import settings

# Set log_config=None to not use the uvicorn logging configuration, and use ours instead.
uvicorn.run(
    app,
    host="0.0.0.0",
    port=settings().server.port,
    log_config=None,
    ssl_keyfile= "/Users/owner/Projects/u-GPT/privkey.pem",  # Add the path to your SSL key file
    ssl_certfile="/Users/owner/Projects/u-GPT/fullchain.pem"  # Add the path to your SSL certificate file
)
