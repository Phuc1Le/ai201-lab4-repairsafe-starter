# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine maintenance and low-risk repairs that most homeowners can complete with basic tools and patience. No permit or professional license required. If this repair goes wrong, the worst case is cosmetic damage or a broken fixture — not injury, fire, or flooding.
```

**caution:**
```
Repairs doable for a motivated homeowner, but where mistakes have real cost or mild risk of injury. No permit is typically required, but the repair involves systems — water or electricity — where something can go meaningfully wrong.
```

**refuse:**
```
Repairs where an amateur mistake can cause fire, flooding, structural damage, serious injury, or death — or where local building codes require a licensed professional and a permit. Do not provide DIY instructions for these.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
We'll add 2 examples (1 positive case and 1 edge case) for each definition. Ask the LLM to reason step-by-step in the 'reason' field.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
json {
    'tier': ....,
    'reason': [step1, step2, ...]
}
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
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
```

**User message:**
```
Classify the following home repair question according to the safety tiers above.

Question:
{question}
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Ask one question: if this repair goes wrong, can it cause fire, flooding, structural failure, injury, or death? If yes: refuse. If the worst case is a leaky pipe or a broken fixture: caution.

Examples:

"How do I replace an outlet that stopped working?"	caution -- Existing circuit, same location, component swap — worst case is a tripped breaker

"How do I add a new outlet to my garage?"	refuse -- Requires opening the panel, running new wire, pulling a permit — amateur mistake = fire hazard discovered years later
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If the LLM response cannot be parsed as valid JSON or the returned tier is not one of `VALID_TIERS`, the function will **fail closed** by returning:
{
    "tier": "caution",
    "reason": "Unable to reliably classify the repair question due to an invalid LLM response."
}

Choosing `"caution"` as the fallback is safer than defaulting to `"safe"`. An invalid or malformed model response indicates uncertainty, and incorrectly labeling a potentially dangerous repair as safe could encourage unsafe DIY work. While this may occasionally over-warn users about harmless repairs, it minimizes the risk of providing unsafe guidance.

```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
[your answer here]
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
[your answer here]
```
