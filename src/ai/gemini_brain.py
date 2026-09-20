"""
Gemini Brain — Central AI Engine for the Instagram Automation System.

ALL AI interactions go through this module. It wraps the official google-genai SDK
and provides methods for every AI capability the system needs.

Models used (all free tier):
- gemini-2.5-flash: Reasoning, content generation, structured output
- gemini-2.5-flash-lite: High-volume, low-cost tasks
- gemini-2.5-flash-image (Nano Banana): Image generation and editing
- gemini-embedding-001: Text embeddings for vector storage

Official SDK: https://ai.google.dev/gemini-api/docs
Python SDK: https://pypi.org/project/google-genai/
"""

import io
import json
import time
from typing import Optional, Type

from google import genai
from google.genai import types
from pydantic import BaseModel
from PIL import Image

from src.config.settings import SETTINGS
from src.core.logging_config import get_logger, log_error

logger = get_logger("ai.gemini_brain")


class GeminiBrain:
    """
    Central Gemini AI client for all AI operations.

    Usage:
        brain = GeminiBrain()
        result = brain.generate_text("Write a caption about AI")
        image = brain.generate_image("A futuristic AI robot")
        embedding = brain.embed_text("Some text to embed")
        search_result = brain.search_web("latest AI trends 2026")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Brain.

        Args:
            api_key: Gemini API key. Defaults to SETTINGS.GEMINI_API_KEY.
        """
        self._api_key = api_key or SETTINGS.GEMINI_API_KEY
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Get one from: https://aistudio.google.com/app/apikey"
            )

        # Initialize the official client
        # Docs: https://ai.google.dev/gemini-api/docs
        self._client = genai.Client(api_key=self._api_key)

        # Model names from settings
        self._reasoning_model = SETTINGS.GEMINI_REASONING_MODEL
        self._lite_model = SETTINGS.GEMINI_LITE_MODEL
        self._image_model = SETTINGS.GEMINI_IMAGE_MODEL
        self._embedding_model = SETTINGS.GEMINI_EMBEDDING_MODEL

        # Rate limiting
        self._last_request_time = 0.0
        self._min_request_interval = 60.0 / SETTINGS.GEMINI_REQUESTS_PER_MINUTE

        # Retry config
        self._max_retries = 3
        self._base_delay = 1.0  # seconds

        logger.info(
            "GeminiBrain initialized with models: "
            f"reasoning={self._reasoning_model}, "
            f"lite={self._lite_model}, "
            f"image={self._image_model}, "
            f"embedding={self._embedding_model}"
        )

    def _rate_limit(self) -> None:
        """Simple rate limiter to respect API quotas."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _retry(self, operation: str, func, *args, **kwargs):
        """
        Execute a function with exponential backoff retry on transient errors.

        Retries on: rate limits (429), server errors (500, 503),
        and google.api_core errors.

        Args:
            operation: Name for logging (e.g., 'generate_text')
            func: Callable to execute
            *args, **kwargs: Arguments to pass

        Returns:
            The return value of func
        """
        last_error = None
        for attempt in range(self._max_retries):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                # Retry on transient errors only
                is_transient = any(x in error_str for x in [
                    "429", "rate limit", "resource exhausted",
                    "503", "service unavailable", "500", "internal",
                    "deadline exceeded", "timeout",
                ])
                if not is_transient or attempt == self._max_retries - 1:
                    log_error("ai.gemini_brain", operation, e)
                    raise
                delay = self._base_delay * (2 ** attempt)
                logger.warning(
                    "[%s] Transient error (attempt %d/%d): %s. Retrying in %.1fs...",
                    operation, attempt + 1, self._max_retries, type(e).__name__, delay
                )
                time.sleep(delay)
        raise last_error  # Should never reach here

    # ========== Text Generation ==========

    def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> str | BaseModel:
        """
        Generate text using Gemini 2.5 Flash (reasoning model).

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction for context
            temperature: Override default temperature
            max_tokens: Override default max tokens
            schema: Pydantic model for structured JSON output

        Returns:
            Generated text string, or parsed Pydantic model if schema is provided

        Docs: https://ai.google.dev/gemini-api/docs/structured-output
        """
        config = types.GenerateContentConfig(
            temperature=temperature or SETTINGS.GEMINI_DEFAULT_TEMPERATURE,
            max_output_tokens=max_tokens or SETTINGS.GEMINI_MAX_TOKENS,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        if schema:
            config.response_mime_type = "application/json"
            config.response_schema = schema

        def _call():
            return self._client.models.generate_content(
                model=self._reasoning_model,
                contents=prompt,
                config=config,
            )

        response = self._retry("generate_text", _call)

        if schema and response.text:
            return schema.model_validate_json(response.text)

        return response.text or ""

    def generate_text_lite(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text using Gemini 2.5 Flash-Lite (budget model).
        Use for high-volume, low-cost tasks like hashtag scoring, quick checks.

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Override temperature

        Returns:
            Generated text string
        """
        config = types.GenerateContentConfig(
            temperature=temperature or SETTINGS.GEMINI_DEFAULT_TEMPERATURE,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        def _call():
            return self._client.models.generate_content(
                model=self._lite_model,
                contents=prompt,
                config=config,
            )

        response = self._retry("generate_text_lite", _call)
        return response.text or ""

    def generate_creative(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> str | BaseModel:
        """
        Generate creative content with higher temperature.
        Used for captions, stories, hooks — where creativity matters.

        Returns:
            Generated text or parsed schema
        """
        return self.generate_text(
            prompt,
            system_instruction=system_instruction,
            temperature=SETTINGS.GEMINI_CREATIVE_TEMPERATURE,
            schema=schema,
        )

    def analyze(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> str | BaseModel:
        """
        Analytical generation with lower temperature.
        Used for data analysis, strategy recommendations, quality checks.

        Returns:
            Generated text or parsed schema
        """
        return self.generate_text(
            prompt,
            system_instruction=system_instruction,
            temperature=SETTINGS.GEMINI_ANALYSIS_TEMPERATURE,
            schema=schema,
        )

    # ========== Image Generation (Nano Banana) ==========

    def generate_image(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "1:1",
        save_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate an image using Nano Banana (Gemini native image generation).

        Args:
            prompt: Detailed description of the image to generate
            aspect_ratio: Image aspect ratio (1:1, 4:5, 9:16, 16:9)
            save_path: Optional path to save the image file

        Returns:
            Image bytes (PNG format)

        Docs: https://ai.google.dev/gemini-api/docs/image-generation
        """
        def _call():
            return self._client.models.generate_content(
                model=self._image_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

        response = self._retry("generate_image", _call)

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = part.inline_data.data

                if save_path:
                    image = Image.open(io.BytesIO(image_bytes))
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    image.save(save_path, "JPEG", quality=95)
                    logger.info(f"Image saved to {save_path}")

                return image_bytes

        raise ValueError("No image was generated in the response")

    def edit_image(
        self,
        image_bytes: bytes,
        instruction: str,
        *,
        save_path: Optional[str] = None,
    ) -> bytes:
        """
        Edit an existing image using Nano Banana.

        Args:
            image_bytes: Original image bytes
            instruction: What to change about the image
            save_path: Optional path to save the edited image

        Returns:
            Edited image bytes

        Docs: https://ai.google.dev/gemini-api/docs/image-generation
        """
        self._rate_limit()

        try:
            # Create image part from bytes
            image = Image.open(io.BytesIO(image_bytes))

            response = self._client.models.generate_content(
                model=self._image_model,
                contents=[instruction, image],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    edited_bytes = part.inline_data.data

                    if save_path:
                        edited_image = Image.open(io.BytesIO(edited_bytes))
                        if edited_image.mode in ("RGBA", "P"):
                            edited_image = edited_image.convert("RGB")
                        edited_image.save(save_path, "JPEG", quality=95)
                        logger.info(f"Edited image saved to {save_path}")

                    return edited_bytes

            raise ValueError("No edited image in the response")

        except Exception as e:
            log_error("ai.gemini_brain", "edit_image", e, context={"instruction": instruction[:100]})
            raise

    # ========== Embeddings ==========

    def embed_text(self, text: str) -> list[float]:
        """
        Generate text embeddings using Gemini Embeddings model.
        Used for vector storage in ChromaDB for memory/knowledge retrieval.

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector)

        Docs: https://ai.google.dev/gemini-api/docs/models/gemini-embedding-001
        """
        self._rate_limit()

        try:
            response = self._client.models.embed_content(
                model=self._embedding_model,
                contents=text,
            )
            return response.embeddings[0].values

        except Exception as e:
            log_error("ai.gemini_brain", "embed_text", e)
            raise

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        self._rate_limit()

        try:
            response = self._client.models.embed_content(
                model=self._embedding_model,
                contents=texts,
            )
            return [e.values for e in response.embeddings]

        except Exception as e:
            log_error("ai.gemini_brain", "embed_batch", e, context={"count": len(texts)})
            raise

    # ========== Web Search (Google Search Grounding) ==========

    def search_web(
        self,
        query: str,
        *,
        system_instruction: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> str | BaseModel:
        """
        Search the web using Gemini's built-in Google Search grounding tool.

        This allows Gemini to search Google in real-time and ground its response
        in current web data — replacing the need for Perplexity or web scrapers.

        Args:
            query: The search query / question
            system_instruction: Optional system prompt
            schema: Optional Pydantic schema for structured output

        Returns:
            Gemini's response grounded in current web search results

        Docs: https://ai.google.dev/gemini-api/docs/google-search
        """
        self._rate_limit()

        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=SETTINGS.GEMINI_ANALYSIS_TEMPERATURE,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        if schema:
            config.response_mime_type = "application/json"
            config.response_schema = schema

        try:
            response = self._client.models.generate_content(
                model=self._reasoning_model,
                contents=query,
                config=config,
            )

            if schema and response.text:
                return schema.model_validate_json(response.text)

            return response.text or ""

        except Exception as e:
            log_error("ai.gemini_brain", "search_web", e, context={"query": query[:100]})
            raise

    # ========== Vision (Image Analysis) ==========

    def analyze_image(
        self,
        image_bytes: bytes,
        question: str,
        *,
        schema: Optional[Type[BaseModel]] = None,
    ) -> str | BaseModel:
        """
        Analyze an image using Gemini's multimodal capabilities.

        Args:
            image_bytes: Image to analyze
            question: What to analyze about the image
            schema: Optional structured output schema

        Returns:
            Analysis text or parsed schema
        """
        self._rate_limit()

        image = Image.open(io.BytesIO(image_bytes))

        config = types.GenerateContentConfig(
            temperature=SETTINGS.GEMINI_ANALYSIS_TEMPERATURE,
        )

        if schema:
            config.response_mime_type = "application/json"
            config.response_schema = schema

        try:
            response = self._client.models.generate_content(
                model=self._reasoning_model,
                contents=[question, image],
                config=config,
            )

            if schema and response.text:
                return schema.model_validate_json(response.text)

            return response.text or ""

        except Exception as e:
            log_error("ai.gemini_brain", "analyze_image", e, context={"question": question[:100]})
            raise

    # ========== Function Calling (Agentic Workflows) ==========

    def function_call(
        self,
        prompt: str,
        tools: list[dict],
        *,
        system_instruction: Optional[str] = None,
        auto_execute: bool = False,
        tool_handlers: Optional[dict] = None,
    ) -> dict:
        """
        Use Gemini Function Calling for agentic workflows.

        Gemini analyzes the prompt and decides which tool(s) to call.
        This enables autonomous AI behavior where the model picks the
        right action (research, generate, publish, analyze) based on
        the user's goal.

        Args:
            prompt: Natural language instruction (e.g., "Research AI trends and create a post")
            tools: List of tool declarations (function name, description, parameters)
            system_instruction: Optional system prompt
            auto_execute: If True, automatically execute the tools and feed results back
            tool_handlers: Dict mapping function names to actual Python callables
                           Required if auto_execute=True

        Returns:
            Dict with 'function_calls' (what Gemini wants to call) and
            'final_response' (text after tool execution, if auto_execute=True)

        Docs: https://ai.google.dev/gemini-api/docs/function-calling
        """
        # Build tool declarations
        function_declarations = []
        for tool in tools:
            function_declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool.get("parameters", {}),
                )
            )

        config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=function_declarations)],
            temperature=SETTINGS.GEMINI_DEFAULT_TEMPERATURE,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        def _call():
            return self._client.models.generate_content(
                model=self._reasoning_model,
                contents=prompt,
                config=config,
            )

        response = self._retry("function_call", _call)

        # Extract function calls from response
        calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    calls.append({
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args) if part.function_call.args else {},
                    })

        result = {"function_calls": calls, "final_response": None}

        # Auto-execute: call the handlers and feed results back to Gemini
        if auto_execute and tool_handlers and calls:
            tool_results = []
            for call in calls:
                handler = tool_handlers.get(call["name"])
                if handler:
                    try:
                        output = handler(**call["args"])
                        tool_results.append({
                            "name": call["name"],
                            "result": str(output),
                        })
                        logger.info("Tool executed: %s", call["name"])
                    except Exception as e:
                        tool_results.append({
                            "name": call["name"],
                            "error": str(e),
                        })
                        log_error("ai.gemini_brain", f"function_call.{call['name']}", e)

            # Feed results back to Gemini for final response
            tool_response_text = json.dumps(tool_results, default=str)
            follow_up = self.generate_text(
                f"Tool execution results:\n{tool_response_text}\n\nBased on these results, provide a summary.",
                system_instruction=system_instruction,
            )
            result["final_response"] = follow_up

        elif not calls and response.text:
            result["final_response"] = response.text

        return result

    # ========== Utility Methods ==========

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        def _call():
            return self._client.models.count_tokens(
                model=self._reasoning_model,
                contents=text,
            )

        response = self._retry("count_tokens", _call)
        return response.total_tokens

    def health_check(self) -> dict:
        """
        Verify the Gemini API is accessible and working.

        Returns:
            Dict with status and model availability
        """
        results = {}
        try:
            # Test reasoning model
            response = self._client.models.generate_content(
                model=self._reasoning_model,
                contents="Say 'OK' if you can read this.",
            )
            results["reasoning"] = bool(response.text)
        except Exception as e:
            results["reasoning"] = False
            results["reasoning_error"] = str(e)

        try:
            # Test embedding model
            response = self._client.models.embed_content(
                model=self._embedding_model,
                contents="test",
            )
            results["embedding"] = len(response.embeddings) > 0
        except Exception as e:
            results["embedding"] = False
            results["embedding_error"] = str(e)

        results["all_ok"] = all(
            results.get(k) for k in ["reasoning", "embedding"]
        )
        return results
