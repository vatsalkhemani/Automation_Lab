import json
import logging

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_ARTICLES_FOR_DIGEST

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are an AI news editor producing a concise daily digest email.

Given a list of AI news articles (with titles, sources, URLs, and descriptions), produce a digest with these rules:

1. Select the TOP 8-12 most important/interesting stories. Prioritize: major product launches, significant research breakthroughs, industry-shaping business moves, and notable policy/regulation news. Skip minor updates, listicles, and opinion pieces.

2. For each selected story, output a JSON object with:
   - "title": A clear, concise headline (rewrite if the original is clickbaity)
   - "source": The original publication name
   - "url": The original article URL
   - "summary": A 2-3 sentence summary that captures the key facts. Be specific: include names, numbers, dates. No filler.
   - "category": One of ["Product Launch", "Research", "Business", "Policy", "Open Source", "Analysis", "Other"]

3. Order stories by importance (most important first).

4. Return ONLY a valid JSON array of objects. No markdown, no commentary, no wrapper text."""


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
                "max_output_tokens": 4096,
            },
        )

        response_text = response.text.strip()
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        digest = json.loads(response_text)

        if not isinstance(digest, list):
            logger.error("Gemini response is not a JSON array. Falling back.")
            return _fallback_summaries(articles_to_send)

        logger.info("Gemini produced %d digest entries.", len(digest))
        return digest

    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini response as JSON: %s", e)
        return _fallback_summaries(articles_to_send)
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return _fallback_summaries(articles_to_send)


def _fallback_summaries(articles: list[dict]) -> list[dict]:
    """Fallback: return articles with their descriptions as summaries (no LLM)."""
    return [
        {
            "title": a["title"],
            "source": a["source"],
            "url": a["url"],
            "summary": a.get("description", "No summary available."),
            "category": "Other",
        }
        for a in articles[:12]
    ]
