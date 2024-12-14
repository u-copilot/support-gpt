"""FastAPI app creation, logger configuration and main API routes."""

import llama_index

from u_copilot.di import global_injector
from u_copilot.launcher import create_app

# Add LlamaIndex simple observability
llama_index.set_global_handler("simple")

app = create_app(global_injector)
