import json
import logging
import re

from google import genai
from google.genai.types import ThinkingConfig

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_ARTICLES_FOR_DIGEST

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are an AI news editor producing a daily digest for a product manager who works in tech.

Given a list of AI news articles, select the TOP 10 most important stories and produce a structured digest.

PRIORITY ORDER for story selection:
1. New product launches and feature releases (especially from OpenAI, Anthropic/Claude, Google/Gemini, Meta, Microsoft, Perplexity, Mistral)
2. Trending AI apps, tools, or demos gaining traction on social media
3. Major funding rounds, acquisitions, and business moves
4. Significant research breakthroughs with real-world implications
5. Policy, regulation, and safety news
6. Industry analysis and notable opinion from credible voices

SKIP these aggressively:
- ALL PyPI/npm/GitHub package releases and library version bumps — no exceptions
- Niche developer tools with no mainstream traction
- Promotional/sponsored content and spam
- Listicles and generic "top 10" articles
- Job postings and event ticket promotions
- Stories with no real substance or news value
- Sources like pypi.org, npmjs.com, or package registries

For each story, output a JSON object with:
- "title": A clear, factual headline. NO clickbait. Rewrite vague titles to state what actually happened. Bad: "Sam Altman would like to remind you..." Good: "Altman Defends AI Energy Use, Compares to Human Caloric Cost"
- "source": The original publication name
- "url": The original article URL
- "takeaways": An array of exactly 3 short bullet strings. Each bullet is one key fact or insight (max 15 words each). Be specific: names, numbers, dates. No filler, no fluff.
- "category": One of ["Product Launch", "Research", "Business", "Policy", "Open Source", "Trending", "Analysis"]

Order stories by importance (most important first).

Return ONLY a valid JSON array. No markdown, no commentary, no wrapper."""


def summarize(articles: list[dict]) -> list[dict]:
    """
    Use Gemini to summarize and curate the top articles.
    Returns a list of dicts with: title, source, url, summary, category.
    """
    if not GEMINI_API_KEY:
        logger.error(
            "GEMINI_API_KEY not set. Returning raw articles without summarization."
        )
        return _fallback_summaries(articles)

    if not articles:
        logger.warning("No articles to summarize.")
        return []

    articles_to_send = articles[:MAX_ARTICLES_FOR_DIGEST]

    articles_text = json.dumps(
        [
            {
                "title": a["title"],
                "source": a["source"],
                "url": a["url"],
                "description": a["description"],
            }
            for a in articles_to_send
        ],
        indent=2,
    )

    user_prompt = (
        f"Here are today's AI news articles. Produce the digest.\n\n{articles_text}"
    )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": 0.3,
                "max_output_tokens": 16384,
                "thinking_config": ThinkingConfig(thinking_budget=0),
            },
        )

        response_text = response.text.strip()
        digest = _parse_json_response(response_text)

        if digest is None:
            logger.error("Could not parse Gemini response. Falling back.")
            return _fallback_summaries(articles_to_send)

        logger.info("Gemini produced %d digest entries.", len(digest))
        return digest
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return _fallback_summaries(articles_to_send)


def _parse_json_response(text: str) -> list[dict] | None:
    """Extract and parse a JSON array from LLM response, with auto-repair."""
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())

    # Extract the JSON array
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return None
    json_str = match.group(0)

    # Attempt 1: parse as-is
    try:
        result = json.loads(json_str)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Attempt 2: fix trailing commas and retry
    fixed = re.sub(r",\s*([}\]])", r"\1", json_str)
    try:
        result = json.loads(fixed)
        if isinstance(result, list):
            logger.info("Parsed JSON after fixing trailing commas.")
            return result
    except json.JSONDecodeError:
        pass

    # Attempt 3: truncated response — try to salvage complete objects
    # Find the last complete object (ending with }) before the parse fails
    last_brace = json_str.rfind("}")
    if last_brace > 0:
        truncated = json_str[: last_brace + 1] + "]"
        truncated = re.sub(r",\s*\]", "]", truncated)
        try:
            result = json.loads(truncated)
            if isinstance(result, list) and len(result) > 0:
                logger.info("Salvaged %d entries from truncated JSON.", len(result))
                return result
        except json.JSONDecodeError:
            pass

    logger.error("All JSON parse attempts failed.")
    return None


def _fallback_summaries(articles: list[dict]) -> list[dict]:
    """Fallback: return articles with their descriptions as takeaways (no LLM)."""
    return [
        {
            "title": a["title"],
            "source": a["source"],
            "url": a["url"],
            "takeaways": [a.get("description", "No summary available.")],
            "category": "Other",
        }
        for a in articles[:10]
    ]
