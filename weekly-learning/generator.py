import json
import logging
import re

from google import genai
from google.genai.types import ThinkingConfig

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are a clear, engaging writer producing a weekly knowledge article for a curious product manager.

Given a CATEGORY, pick a big, widely-relevant topic — something every curious person should know about. Then write a clear explainer that makes the reader feel smarter after reading it.

Topic selection:
- Pick foundational, mainstream topics. Not niche or obscure.
- Good examples: "How GPS actually works", "The story of apartheid and Nelson Mandela", "What is quantum computing", "The history of Buddhism", "Why we dream", "How inflation works", "The basics of evolution", "What started World War I".
- Bad examples: "The Library of Ashurbanipal", "The Great Emu War", "Obscure medieval trade routes". Too niche — most people would not encounter these.
- Think: "What would a well-rounded person want to understand?"

Writing style:
- Write like you're explaining it to a smart friend over coffee. Conversational, not academic.
- Short paragraphs — 2 to 4 sentences max per paragraph. No walls of text.
- Use plain, direct language. If a simpler word works, use it. Avoid jargon unless you explain it immediately.
- Be concrete — names, dates, numbers — but weave them into the narrative naturally. Don't just dump facts.
- Use the structure: what happened / how it works → why it matters → what most people get wrong or don't know.
- The reader should finish and think "I actually get this now."
- Aim for ~1000 words across all sections.

Return a JSON object with this exact structure:
{
  "topic": "The specific topic name",
  "category": "The category it belongs to",
  "hook": "A 2-3 sentence opening that tells the reader why this topic matters and what they will learn.",
  "sections": [
    {
      "heading": "Short, clear section title",
      "content": "2-3 short paragraphs. Each paragraph is 2-4 sentences."
    }
  ],
  "surprising_fact": "One genuinely surprising or counterintuitive fact about this topic (1-2 sentences).",
  "further_reading": [
    "Book, article, video, or podcast suggestion 1",
    "Book, article, video, or podcast suggestion 2",
    "Book, article, video, or podcast suggestion 3"
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

    user_prompt = f"Category: {category}\n\nPick a big, mainstream topic within this category — something important that a well-rounded person should understand. Write a clear, conversational explainer."

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
