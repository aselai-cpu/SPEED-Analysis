"""Service for interacting with Claude API"""

import anthropic
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Service for interacting with Claude API
    Handles all AI text generation for planning and rendering
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not found in environment")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> str:
        """
        Generate text using Claude

        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system: Optional system prompt

        Returns:
            Generated text response
        """
        if not self.client:
            raise Exception("Claude API client not initialized. Check ANTHROPIC_API_KEY")

        try:
            logger.info("🤖 CLAUDE API REQUEST")
            logger.info("-"*60)
            logger.info(f"Model: {self.model}")
            logger.info(f"Max Tokens: {max_tokens}")
            logger.info(f"Temperature: {temperature}")

            if system:
                logger.info(f"System Prompt:\n{system}")

            # Log full prompt
            logger.info(f"User Prompt:\n{prompt}")
            logger.info("-"*60)

            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system:
                kwargs["system"] = system

            logger.info("⏳ Sending request to Claude API...")

            message = self.client.messages.create(**kwargs)

            response_text = message.content[0].text

            logger.info("✅ CLAUDE API RESPONSE")
            logger.info("-"*60)
            logger.info(f"Input Tokens: {message.usage.input_tokens}")
            logger.info(f"Output Tokens: {message.usage.output_tokens}")
            logger.info(f"Response Length: {len(response_text)} characters")

            # Log full response
            logger.info(f"Response:\n{response_text}")
            logger.info("-"*60)

            return response_text

        except Exception as e:
            logger.error("❌ CLAUDE API ERROR")
            logger.error("-"*60)
            logger.error(f"Error: {str(e)}")
            logger.error("-"*60)
            raise Exception(f"Claude API error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Claude API is accessible"""
        return self.client is not None and self.api_key is not None
