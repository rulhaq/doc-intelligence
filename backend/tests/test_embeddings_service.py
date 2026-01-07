import os
import importlib
import unittest
from unittest.mock import AsyncMock, patch


def _set_required_env(provider: str):
    os.environ["APP_ENV"] = "test"
    os.environ["DEBUG"] = "false"
    os.environ["BACKEND_HOST"] = "0.0.0.0"
    os.environ["BACKEND_PORT"] = "8000"
    os.environ["BACKEND_URL"] = "http://backend"
    os.environ["FRONTEND_URL"] = "http://frontend"
    os.environ["DATABASE_URL"] = "postgresql://u:p@db:5432/db"
    os.environ["REDIS_URL"] = "redis://redis:6379/0"
    os.environ["QDRANT_URL"] = "http://qdrant:6333"
    os.environ["STORAGE_MODE"] = "pvc"
    os.environ["FILE_STORAGE_PATH"] = "/data"
    os.environ["VLLM_BASE_URL"] = "http://vllm"
    os.environ["VLLM_MODEL"] = "chat-model"
    os.environ["VLLM_API_TOKEN"] = "token"
    os.environ["OCR_WORKER_URL"] = "http://ocr"
    os.environ["SECRET_KEY"] = "secret_key_1234567890"
    os.environ["CORS_ORIGINS"] = "http://frontend"
    os.environ["EMBEDDINGS_PROVIDER"] = provider
    os.environ["TEI_BASE_URL"] = "http://tei:8080"
    os.environ["TEI_TIMEOUT"] = "60"
    os.environ["VLLM_EMBEDDING_BASE_URL"] = "http://vllm-embed"
    os.environ["VLLM_EMBEDDING_MODEL"] = "embed-model"


class EmbeddingsServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_vllm_routes(self):
        _set_required_env("vllm")
        import app.core.config as config
        importlib.reload(config)
        import app.services.embeddings_service as service
        importlib.reload(service)
        service.get_embeddings_service.cache_clear()

        with patch.object(service.EmbeddingsService, "_embed_with_vllm", new_callable=AsyncMock) as mock_vllm:
            mock_vllm.return_value = [[0.1, 0.2]]
            result = await service.embed_query("hello")
            self.assertEqual(result, [0.1, 0.2])
            mock_vllm.assert_awaited_once()

    async def test_provider_tei_routes(self):
        _set_required_env("tei")
        import app.core.config as config
        importlib.reload(config)
        import app.services.embeddings_service as service
        importlib.reload(service)
        service.get_embeddings_service.cache_clear()

        with patch.object(service.EmbeddingsService, "_embed_with_tei", new_callable=AsyncMock) as mock_tei:
            mock_tei.return_value = [[0.3, 0.4]]
            result = await service.embed_query("مرحبا")
            self.assertEqual(result, [0.3, 0.4])
            mock_tei.assert_awaited_once()

    async def test_parse_tei_response_list(self):
        _set_required_env("tei")
        import app.core.config as config
        importlib.reload(config)
        import app.services.embeddings_service as service
        importlib.reload(service)
        svc = service.EmbeddingsService()

        class DummyResponse:
            def json(self):
                return [[0.1, 0.2]]

        vectors = svc._parse_tei_response(DummyResponse())
        self.assertEqual(vectors, [[0.1, 0.2]])

    async def test_parse_tei_response_dict_embeddings(self):
        _set_required_env("tei")
        import app.core.config as config
        importlib.reload(config)
        import app.services.embeddings_service as service
        importlib.reload(service)
        svc = service.EmbeddingsService()

        class DummyResponse:
            def json(self):
                return {"embeddings": [[0.5, 0.6]]}

        vectors = svc._parse_tei_response(DummyResponse())
        self.assertEqual(vectors, [[0.5, 0.6]])

    async def test_missing_tei_base_url_fails_fast(self):
        _set_required_env("tei")
        os.environ.pop("TEI_BASE_URL", None)
        with self.assertRaises(ValueError):
            import app.core.config as config
            importlib.reload(config)
            import app.services.embeddings_service as service
            importlib.reload(service)
            service.get_embeddings_service.cache_clear()
            service.EmbeddingsService()


if __name__ == "__main__":
    unittest.main()
