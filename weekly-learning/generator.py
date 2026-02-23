import json
import logging
import re

from google import genai
from google.genai.types import ThinkingConfig

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are a brilliant, curious writer producing a weekly deep-dive article for a product manager who loves learning.

Given a CATEGORY, pick a specific, non-obvious topic within it and write an engaging exploration.

Guidelines:
- Pick something surprising or lesser-known — not the obvious first result. Example: for "History & Civilization", don't write about World War II; write about the Library of Ashurbanipal or the Great Emu War.
- Write for someone smart but not an expert in this field. Explain concepts clearly.
- Be concrete: use names, dates, numbers, places. No vague filler.
- Aim for ~800 words total across all sections.
- Make it a satisfying Saturday morning read — informative, surprising, and well-paced.

Return a JSON object with this exact structure:
{
  "topic": "The specific topic name",
  "category": "The category it belongs to",
  "hook": "An opening paragraph (2-3 sentences) that grabs attention and sets up why this topic matters.",
  "sections": [
    {
      "heading": "Section title",
      "content": "2-3 paragraphs of content for this section."
    }
  ],
  "surprising_fact": "One surprising or counterintuitive fact related to the topic (1-2 sentences).",
  "further_reading": [
    "Book, article, or resource suggestion 1",
    "Book, article, or resource suggestion 2",
    "Book, article, or resource suggestion 3"
  ]
}

Produce exactly 3-4 sections. Return ONLY valid JSON. No markdown, no commentary, no wrapper."""


def generate_topic(category: str) -> dict | None:
    """
    Use Gemini to generate a deep-dive article on a topic within the given category.
    Returns a dict with: topic, category, hook, sections, surprising_fact, further_reading.
    Returns None on failure.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set. Cannot generate content.")
        return None

    user_prompt = f"Category: {category}\n\nPick a fascinating topic within this category and write the deep-dive article."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": 0.9,
                "max_output_tokens": 16384,
                "thinking_config": ThinkingConfig(thinking_budget=0),
            },
        )

        response_text = response.text.strip()
        article = _parse_json_response(response_text)

        if article is None:
            logger.error("Could not parse Gemini response.")
            return None

        logger.info("Generated article: '%s' in category '%s'.", article.get("topic"), article.get("category"))
        return article

    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None


def _parse_json_response(text: str) -> dict | None:
    """Extract and parse a JSON object from LLM response, with auto-repair."""
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())

    # Extract the JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    json_str = match.group(0)

    # Attempt 1: parse as-is
    try:
        result = json.loads(json_str)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Attempt 2: fix trailing commas and retry
    fixed = re.sub(r",\s*([}\]])", r"\1", json_str)
    try:
        result = json.loads(fixed)
        if isinstance(result, dict):
            logger.info("Parsed JSON after fixing trailing commas.")
            return result
    except json.JSONDecodeError:
        pass

    logger.error("All JSON parse attempts failed.")
    return None
