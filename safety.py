from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS
import json
_client = Groq(api_key=GROQ_API_KEY)
VALID_TIERS = {"safe", "caution", "refuse"}
SYSTEM_PROMPT = """
You are a home repair safety classifier. Your task is to classify a user's home repair question into one of three safety tiers based on the potential risk of performing the repair without professional assistance.

Definitions:

safe: Routine maintenance and low-risk repairs that most homeowners can complete with basic tools and patience. No permit or professional license is typically required. Mistakes are unlikely to cause injury, fire, flooding, or major property damage.

Example:

"How do I patch a small hole in drywall?" → safe
Edge case: "How do I replace a cabinet handle?" → safe

caution: Repairs that an experienced or careful homeowner may perform, but mistakes can result in property damage or minor injury. These commonly involve plumbing, electrical fixtures, or other household systems, but generally do not require a permit.

Example:

"How do I replace a bathroom faucet?" → caution
Edge case: "Can I replace my own electrical outlet?" → caution

refuse: Repairs where incorrect work could cause fire, flooding, structural damage, gas leaks, serious injury, or death, or that typically require permits or licensed professionals. Do not encourage DIY instructions for these tasks.

Example:

"How do I replace my electrical service panel?" → refuse
Edge case: "Can I remove a load-bearing wall?" → refuse

Important classification rules:

- For electrical work, replacing an existing fixture, switch, or outlet in the same location is classified as "caution".
- Any repair that requires moving an electrical fixture to a new location, extending or rerouting wiring, installing new circuits, or modifying permanent household wiring is classified as "refuse", regardless of how small the physical distance is.
- Classify based on the type of work required, not how easy or minor the user describes it ("just", "only", "tiny change", etc.).

Caution/refuse boundary:
Ask one question: if this repair goes wrong, can it cause fire, flooding, structural failure, injury, or death? If yes: refuse. If the worst case is a leaky pipe or a broken fixture: caution.

For every question:
Identify the repair being requested.
Consider the potential consequences if performed incorrectly.
Compare the repair against the tier definitions.
Select exactly one tier.

Respond only with valid JSON in this format:

{
  "tier": "safe | caution | refuse",
  "reason": [
    "Step 1 reasoning",
    "Step 2 reasoning",
    "Step 3 reasoning"
  ]
}

Do not include markdown, explanations outside the JSON, or any additional fields.
"""
def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Question:\n{question}",
                },
            ],
        )

        raw = response.choices[0].message.content.strip()

        parsed = json.loads(raw)

        tier = parsed.get("tier", "").lower()

        if tier not in VALID_TIERS:
            raise ValueError("Invalid tier")

        reason = parsed.get("reason", "")

        if isinstance(reason, list):
            reason = "; ".join(reason)

        return {
            "tier": tier,
            "reason": reason,
        }

    except Exception:
        return {
            "tier": "caution",
            "reason": "Unable to reliably classify the repair question due to an invalid LLM response.",
        }
