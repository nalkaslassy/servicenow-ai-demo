import anthropic
import json
import re
from app.config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def _extract_json(text: str) -> dict:
    """Extract JSON from response even if wrapped in markdown code fences."""
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text)

def get_specialist_guidance(description: str, resolved_tickets: list) -> dict:
    # Truncate resolution_notes to keep prompt within Haiku's context window
    def summarise(t):
        notes = (t.resolution_notes or "")[:400]
        resolution = (t.resolution or "")[:300]
        return (
            f"Ticket: {t.ticket_number}\n"
            f"Title: {t.title}\n"
            f"Category: {t.category}\n"
            f"Tags: {t.tags}\n"
            f"Resolution: {resolution}\n"
            f"Steps taken: {notes}"
        )

    ticket_summaries = "\n\n---\n\n".join([summarise(t) for t in resolved_tickets])

    prompt = f"""You are an IT support AI assistant helping a support specialist resolve an open ticket.
The specialist has described the symptoms below. Using the past resolved tickets as your knowledge base,
give them a clear actionable playbook telling them exactly what to do.

SPECIALIST'S ISSUE:
{description}

PAST RESOLVED TICKETS (knowledge base):
{ticket_summaries}

Return a JSON object with this exact structure:
{{
  "likely_issue": "One sentence — what this issue most likely is",
  "confidence": "High" or "Medium" or "Low",
  "guidance": [
    "Step 1: specific action",
    "Step 2: next action",
    "Step 3: etc"
  ],
  "referenced_tickets": ["INC0000XXX", "INC0000YYY"],
  "escalation_needed": true or false,
  "escalation_team": "Exact team name if needed, else null",
  "escalation_instructions": "How to escalate — what system, what info to include, else null",
  "estimated_resolution_time": "e.g. 30 minutes, 2 hours, 1 business day",
  "warning": "Important caution the specialist must know, or null"
}}

Rules:
- Only reference tickets directly relevant to this issue.
- If past tickets involved opening a request with another team, include exactly how in escalation_instructions.
- Guidance steps must be specific and actionable — not generic advice.
- If no past tickets match, still provide general guidance based on the issue type.
Return ONLY valid JSON with no markdown."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return _extract_json(response.content[0].text)
    except Exception as e:
        print(f"[ai_service] JSON parse error: {e}")
        print(f"[ai_service] Raw response: {response.content[0].text[:500]}")
        return {
            "likely_issue": "Unable to determine — review symptoms carefully.",
            "confidence": "Low",
            "guidance": ["Review the ticket description.", "Search for similar past tickets manually.", "Escalate to your team lead if unsure."],
            "referenced_tickets": [],
            "escalation_needed": False,
            "escalation_team": None,
            "escalation_instructions": None,
            "estimated_resolution_time": "Unknown",
            "warning": None
        }


def find_similar_tickets(user_description: str, resolved_tickets: list) -> dict:
    ticket_summaries = "\n\n".join([
        f"Ticket: {t.ticket_number}\n"
        f"Title: {t.title}\n"
        f"Description: {t.description}\n"
        f"Category: {t.category}\n"
        f"Resolution: {t.resolution}\n"
        f"Tags: {t.tags}"
        for t in resolved_tickets
    ])

    prompt = f"""You are an IT support AI assistant. A user has described an issue.
Your job is to find the most similar past resolved tickets from our database.

USER ISSUE:
{user_description}

RESOLVED TICKETS DATABASE:
{ticket_summaries}

Return a JSON object with this exact structure:
{{
  "matches": [
    {{
      "ticket_number": "INC...",
      "similarity_score": 0-100,
      "reason": "One sentence explaining why this matches",
      "confidence": "High" | "Medium" | "Low"
    }}
  ],
  "top_category": "Network|Software|Hardware|Access|Email|Security",
  "summary": "One sentence describing what the user's issue appears to be"
}}

Return at most 3 matches. Only include tickets with similarity_score >= 30.
If no tickets match well, return an empty matches array.
Return ONLY valid JSON, no markdown, no explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.content[0].text)
    except Exception:
        return {"matches": [], "top_category": "Software", "summary": user_description}


def classify_new_ticket(description: str, teams: list) -> dict:
    team_descriptions = "\n".join([
        f"- {t.name}: {t.description} (avg resolution: {t.avg_resolution_hours}h)"
        for t in teams
    ])

    prompt = f"""You are an IT support AI. Classify this new support issue and route it to the correct team.

USER ISSUE:
{description}

AVAILABLE TEAMS:
{team_descriptions}

Return a JSON object with this exact structure:
{{
  "title": "Short descriptive title (max 10 words)",
  "category": "Network|Software|Hardware|Access|Email|Security",
  "priority": "P1|P2|P3|P4",
  "assigned_team": "Exact team name from the list above",
  "priority_reason": "One sentence explaining the priority",
  "routing_reason": "One sentence explaining why this team"
}}

Priority guide: P1=critical/security/complete outage, P2=significant impact/multiple users, P3=single user/workaround exists, P4=minor/cosmetic.
Return ONLY valid JSON."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.content[0].text)
    except Exception:
        return {
            "title": description[:60],
            "category": "Software",
            "priority": "P3",
            "assigned_team": "Software Support",
            "priority_reason": "Standard priority assigned.",
            "routing_reason": "Routed to Software Support as default."
        }


def suggest_next_action(ticket) -> dict:
    prompt = f"""You are an IT support coaching AI. A specialist just received this ticket and needs their immediate next action.

TICKET:
Number: {ticket.ticket_number}
Title: {ticket.title}
Description: {ticket.description}
Category: {ticket.category}
Priority: {ticket.priority}
Status: {ticket.status}
Assigned Team: {ticket.assigned_team}

Return a JSON object with this exact structure:
{{
  "next_actions": [
    "First specific action the specialist should take RIGHT NOW",
    "Second action after that",
    "Third action or escalation path"
  ],
  "requires_sub_ticket": true or false,
  "sub_ticket_team": "Exact team name if sub-ticket is needed, otherwise null",
  "sub_ticket_reason": "Why a sub-ticket is needed, otherwise null",
  "estimated_resolution_hours": <integer>,
  "risk_level": "Low" or "Medium" or "High",
  "key_questions": [
    "First diagnostic question to ask the user",
    "Second diagnostic question"
  ]
}}

Be specific. Not 'investigate the issue' — tell them exactly what to open, check, or ask first.
If this requires another team (Fund Services, Network, Vendor, etc.), set requires_sub_ticket to true.
Return ONLY valid JSON."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.content[0].text)
    except Exception:
        return {
            "next_actions": [
                "Review the ticket description carefully.",
                "Check for similar resolved tickets in the portal.",
                "Contact the assigned team if no match is found."
            ],
            "requires_sub_ticket": False,
            "sub_ticket_team": None,
            "sub_ticket_reason": None,
            "estimated_resolution_hours": 4,
            "risk_level": "Medium",
            "key_questions": [
                "When did this issue first occur?",
                "Has anything changed recently (updates, new hardware, role change)?"
            ]
        }
