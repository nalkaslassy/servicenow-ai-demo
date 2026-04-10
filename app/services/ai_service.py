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

    prompt = f"""You are an IT support AI assistant. Your ONLY knowledge source is the past resolved tickets provided below.
You must not use any outside knowledge, general IT best practices, or information not present in these tickets.

SPECIALIST'S ISSUE:
{description}

PAST RESOLVED TICKETS (your only knowledge source):
{ticket_summaries}

Instructions:
- Read the past tickets carefully and identify any that are relevant to the specialist's issue.
- If relevant tickets exist, base your guidance ONLY on what those tickets document — the exact steps taken, root causes found, and teams involved.
- If NO past tickets are relevant to this issue, you must say so honestly. Set confidence to "Low", leave referenced_tickets empty, and set likely_issue to "No matching cases found in the knowledge base — this issue has not been seen before."
- Do NOT invent steps, draw on general IT knowledge, or guess at solutions not evidenced by the past tickets.
- Do NOT reference a ticket unless it is directly relevant to this specific issue.

Return a JSON object with this exact structure:
{{
  "likely_issue": "One sentence — what this issue most likely is based on past tickets, or state no match was found",
  "confidence": "High" or "Medium" or "Low",
  "guidance": [
    "Step 1: specific action from past ticket",
    "Step 2: next action",
    "Step 3: etc"
  ],
  "referenced_tickets": ["INC0000XXX", "INC0000YYY"],
  "escalation_needed": true or false,
  "escalation_team": "Exact team name if needed, else null",
  "escalation_instructions": "How to escalate — what system, what info to include, else null",
  "estimated_resolution_time": "e.g. 30 minutes, 2 hours, 1 business day, or null if unknown",
  "warning": "Important caution from past tickets, or null"
}}

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
  "routing_reason": "One sentence explaining why this team",
  "confidence": "High|Medium|Low",
  "key_signals": ["signal phrase from description that drove classification", "another signal", "third signal"]
}}

Priority guide: P1=critical/security/complete outage, P2=significant impact/multiple users, P3=single user/workaround exists, P4=minor/cosmetic.
confidence: High if the issue clearly matches one category, Medium if ambiguous, Low if very vague.
key_signals: 2-4 short phrases from the user's description that most influenced your classification decision.
Return ONLY valid JSON."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return _extract_json(response.content[0].text)
    except Exception:
        return {
            "title": description[:60],
            "category": "Software",
            "priority": "P3",
            "assigned_team": "Software Support",
            "priority_reason": "Standard priority assigned.",
            "routing_reason": "Routed to Software Support as default.",
            "confidence": "Low",
            "key_signals": []
        }


def generate_incident_report(ticket, work_notes: list) -> str:
    notes_text = "\n".join([
        f"[{n.note_type.replace('_', ' ')}] {n.created_at.strftime('%Y-%m-%d %H:%M')} — {n.content}"
        for n in work_notes
    ]) or "No activity notes recorded."

    prompt = f"""Generate a professional post-incident report for this resolved IT support ticket.

TICKET:
Number: {ticket.ticket_number}
Title: {ticket.title}
Category: {ticket.category}
Priority: {ticket.priority}
Team: {ticket.assigned_team}
Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M') if ticket.created_at else 'Unknown'}
Resolved: {ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else 'Unknown'}
Resolution Time: {ticket.resolution_time_hours}h

ISSUE DESCRIPTION:
{ticket.description}

RESOLUTION SUMMARY:
{ticket.resolution or 'Not documented'}

RESOLUTION STEPS:
{ticket.resolution_notes or 'Not documented'}

ACTIVITY LOG:
{notes_text}

Write a professional post-incident report with exactly these sections:
## Executive Summary
## Timeline of Events
## Root Cause
## Resolution Steps Taken
## Business Impact
## Recommendations

Be factual. Base everything only on the information provided. Be concise and professional."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def query_analytics(question: str, analytics_data: dict) -> str:
    data_summary = json.dumps(analytics_data, indent=2, default=str)

    prompt = f"""You are an analytics assistant for an IT support ticket system.
Answer the question using ONLY the data below. Be concise and specific — cite exact numbers from the data.
If the data does not contain enough information to answer, say so clearly.

ANALYTICS DATA:
{data_summary}

QUESTION: {question}

Answer in 1-3 sentences maximum."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def suggest_next_action(ticket, resolved_tickets: list = None) -> dict:
    # Build knowledge base context from similar resolved tickets in the same category
    kb_context = ""
    if resolved_tickets:
        same_cat = [t for t in resolved_tickets if t.category == ticket.category][:10]
        if same_cat:
            summaries = "\n\n".join([
                f"Ticket: {t.ticket_number} | {t.title}\n"
                f"Resolution: {(t.resolution or '')[:200]}\n"
                f"Steps: {(t.resolution_notes or '')[:300]}"
                for t in same_cat
            ])
            kb_context = f"\n\nPAST RESOLVED TICKETS IN THIS CATEGORY (use these to inform your advice):\n{summaries}"

    prompt = f"""You are an IT support coaching AI. A specialist just received this ticket and needs their immediate next action.
Base your advice on the past resolved tickets provided where relevant. Do not invent steps not evidenced by past tickets or the ticket description.

TICKET:
Number: {ticket.ticket_number}
Title: {ticket.title}
Description: {ticket.description}
Category: {ticket.category}
Priority: {ticket.priority}
Status: {ticket.status}
Assigned Team: {ticket.assigned_team}{kb_context}

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
        return _extract_json(response.content[0].text)
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
