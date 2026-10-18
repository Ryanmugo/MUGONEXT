"""
=========================================================
MUGONEXT
Recommendation Prompts
=========================================================

Prompt templates for optional LLM-powered recommendation
generation.

The local recommendation engine does not depend on an LLM.

Author:
MUGONEXT
"""

from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT = """
You are MUGONEXT, an AI business intelligence assistant.

Your job is to interpret validated business forecasting
results and provide practical, conservative, actionable
recommendations.

Rules:
1. Base recommendations only on supplied data.
2. Do not invent business facts.
3. Clearly distinguish forecast evidence from assumptions.
4. Prefer specific actions over generic advice.
5. Consider risk, uncertainty, confidence, and forecast quality.
6. Keep the recommendation understandable to a business owner.
7. Never present a forecast as a guaranteed outcome.
"""


def build_recommendation_prompt(
    analysis: dict[str, Any],
) -> str:
    """
    Build a structured prompt for an LLM.
    """

    payload = json.dumps(
        analysis,
        indent=2,
        default=str,
    )

    return f"""
Analyze the following MUGONEXT forecast intelligence:

{payload}

Return a business recommendation containing:

- title
- category
- recommendation
- reasoning
- expected_outcome
- suggested_action
- priority
- priority_score
- impact_score
- confidence_score
- ai_explanation

Use only the supplied forecast information.
Do not invent revenue, costs, inventory quantities, customer
behavior, or other business facts that are not present.
"""