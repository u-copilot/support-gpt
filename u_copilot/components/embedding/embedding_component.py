import logging

from injector import inject, singleton
from llama_index import MockEmbedding
from llama_index.embeddings.base import BaseEmbedding

from u_copilot.paths import models_cache_path
from u_copilot.settings.settings import Settings

logger = logging.getLogger(__name__)


@singleton
class EmbeddingComponent:
    embedding_model: BaseEmbedding

    @inject
    def __init__(self, settings: Settings) -> None:
        embedding_mode = settings.embedding.mode
        logger.info("Initializing the embedding model in mode=%s", embedding_mode)
        match embedding_mode:
            case "local":
                from llama_index.embeddings import HuggingFaceEmbedding

                self.embedding_model = HuggingFaceEmbedding(
                    model_name=settings.local.embedding_hf_model_name,
                    cache_folder=str(models_cache_path),
                )
            case "sagemaker":

                from u_copilot.components.embedding.custom.sagemaker import (
                    SagemakerEmbedding,
                )

                self.embedding_model = SagemakerEmbedding(
                    endpoint_name=settings.sagemaker.embedding_endpoint_name,
                )
            case "openai":
                from llama_index import OpenAIEmbedding

                openai_settings = settings.openai.api_key
                self.embedding_model = OpenAIEmbedding(api_key=openai_settings)
            case "mock":
                # Not a random number, is the dimensionality used by
                # the default embedding model
                self.embedding_model = MockEmbedding(384)
