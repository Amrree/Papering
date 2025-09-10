"""
LLM Client Module

Provides unified interface for local and remote LLM providers.
Supports Ollama (local) and OpenAI API (remote) with automatic fallback.

Based on patterns from:
- LangChain LLM adapters: https://github.com/langchain-ai/langchain/blob/main/langchain/llms
- OpenAI API integration: https://github.com/openai/openai-python
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

# LLM providers
import openai
import requests

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass
class LLMResponse:
    """Standardized LLM response format."""
    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]


class LLMClient:
    """
    Unified interface for local and remote LLM providers.
    
    Responsibilities:
    - Provider selection and configuration
    - Request/response standardization
    - Automatic fallback between providers
    - Streaming response support
    - Usage tracking and logging
    """
    
    def __init__(self, 
                 default_provider: LLMProvider = LLMProvider.OLLAMA,
                 ollama_url: str = "http://localhost:11434",
                 openai_model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM client.
        
        Args:
            default_provider: Default provider to use
            ollama_url: URL for Ollama server
            openai_model: OpenAI model to use
        """
        self.default_provider = default_provider
        self.ollama_url = ollama_url
        self.openai_model = openai_model
        
        # Initialize providers
        self._init_openai()
        self._init_ollama()
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "provider_usage": {provider.value: 0 for provider in LLMProvider},
            "total_tokens": 0
        }
        
    def _init_openai(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("LLM_REMOTE_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.openai_available = True
            logger.info("OpenAI client initialized")
        else:
            self.openai_available = False
            logger.warning("No OpenAI API key found")
            
    def _init_ollama(self):
        """Initialize Ollama connection."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_available = True
                self.available_models = [model["name"] for model in response.json().get("models", [])]
                logger.info(f"Ollama available with models: {self.available_models}")
            else:
                self.ollama_available = False
                logger.warning("Ollama server not responding")
        except Exception as e:
            self.ollama_available = False
            logger.warning(f"Ollama connection failed: {e}")
            
    def generate(self, 
                prompt: str, 
                provider: Optional[LLMProvider] = None,
                model: Optional[str] = None,
                max_tokens: int = 2000,
                temperature: float = 0.7,
                stream: bool = False) -> LLMResponse:
        """
        Generate text using specified or default provider.
        
        Args:
            prompt: Input prompt
            provider: LLM provider to use
            model: Specific model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream response
            
        Returns:
            LLMResponse with generated content
        """
        provider = provider or self.default_provider
        
        # Try specified provider first, then fallback
        try:
            if provider == LLMProvider.OPENAI and self.openai_available:
                return self._generate_openai(prompt, model, max_tokens, temperature, stream)
            elif provider == LLMProvider.OLLAMA and self.ollama_available:
                return self._generate_ollama(prompt, model, max_tokens, temperature, stream)
            else:
                # Fallback to available provider
                if self.openai_available:
                    logger.info("Falling back to OpenAI")
                    return self._generate_openai(prompt, model, max_tokens, temperature, stream)
                elif self.ollama_available:
                    logger.info("Falling back to Ollama")
                    return self._generate_ollama(prompt, model, max_tokens, temperature, stream)
                else:
                    raise RuntimeError("No LLM providers available")
                    
        except Exception as e:
            logger.error(f"LLM generation failed with {provider.value}: {e}")
            # Try fallback provider
            fallback_provider = LLMProvider.OPENAI if provider == LLMProvider.OLLAMA else LLMProvider.OLLAMA
            if ((fallback_provider == LLMProvider.OPENAI and self.openai_available) or
                (fallback_provider == LLMProvider.OLLAMA and self.ollama_available)):
                logger.info(f"Trying fallback provider: {fallback_provider.value}")
                return self.generate(prompt, fallback_provider, model, max_tokens, temperature, stream)
            else:
                raise
                
    def _generate_openai(self, 
                        prompt: str, 
                        model: Optional[str], 
                        max_tokens: int,
                        temperature: float,
                        stream: bool) -> LLMResponse:
        """Generate text using OpenAI API."""
        model = model or self.openai_model
        
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )
            
            if stream:
                content = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
            else:
                content = response.choices[0].message.content
                
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            self._update_usage_stats(LLMProvider.OPENAI, usage["total_tokens"])
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=model,
                usage=usage,
                metadata={"stream": stream}
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
            
    def _generate_ollama(self, 
                        prompt: str, 
                        model: Optional[str], 
                        max_tokens: int,
                        temperature: float,
                        stream: bool) -> LLMResponse:
        """Generate text using Ollama API."""
        model = model or "llama2"  # Default Ollama model
        
        if model not in self.available_models:
            logger.warning(f"Model {model} not available, using {self.available_models[0] if self.available_models else 'llama2'}")
            model = self.available_models[0] if self.available_models else "llama2"
            
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                stream=stream,
                timeout=300
            )
            response.raise_for_status()
            
            if stream:
                content = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            content += data["response"]
            else:
                data = response.json()
                content = data.get("response", "")
                
            # Ollama doesn't provide detailed usage stats
            usage = {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split())
            }
            
            self._update_usage_stats(LLMProvider.OLLAMA, usage["total_tokens"])
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OLLAMA,
                model=model,
                usage=usage,
                metadata={"stream": stream}
            )
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
            
    def _update_usage_stats(self, provider: LLMProvider, tokens: int):
        """Update usage statistics."""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["provider_usage"][provider.value] += 1
        self.usage_stats["total_tokens"] += tokens
        
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers."""
        providers = []
        if self.openai_available:
            providers.append(LLMProvider.OPENAI)
        if self.ollama_available:
            providers.append(LLMProvider.OLLAMA)
        return providers
        
    def get_available_models(self, provider: LLMProvider) -> List[str]:
        """Get list of available models for provider."""
        if provider == LLMProvider.OPENAI and self.openai_available:
            return ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        elif provider == LLMProvider.OLLAMA and self.ollama_available:
            return self.available_models
        else:
            return []
            
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.usage_stats.copy()
        
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "provider_usage": {provider.value: 0 for provider in LLMProvider},
            "total_tokens": 0
        }
        logger.info("Usage statistics reset")


# Public API methods for LLMClient:
# - generate(prompt, provider, model, max_tokens, temperature, stream) -> LLMResponse
# - get_available_providers() -> List[LLMProvider]
# - get_available_models(provider) -> List[str]
# - get_usage_stats() -> Dict[str, Any]
# - reset_usage_stats() -> None