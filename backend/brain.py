"""LLM reasoning with health context injection and tool use."""

import json
from collections.abc import Iterator

from mistralai.client import Mistral

from backend.config import LLM_MODEL
from backend.health_store import compare_periods, get_correlation, get_latest, get_summary, get_trend

SYSTEM_TEMPLATE = """\
Tu es V.I.T.A.L, un coach bien-être vocal spécialisé dans la prévention du stress \
et du burnout. Tu analyses les données de santé de l'utilisateur pour détecter \
les signaux de stress chronique et l'aider à prévenir l'épuisement professionnel.

{user_profile}

MISSION:
Ta priorité est de détecter les signes de stress et de fatigue accumulée. \
Les indicateurs clés de stress sont :
- HRV basse (< 30 ms) = récupération insuffisante, stress physiologique
- Resting HR élevée (> 80 bpm) = système nerveux en alerte
- Sommeil dégradé (< 6h, peu de profond/REM) = récupération compromise
- Sédentarité (< 5000 pas) = facteur aggravant
- Tendance négative sur plusieurs jours = stress chronique, risque de burnout

REPÈRES (adulte en bonne santé):
- Fréquence cardiaque repos : 60-100 bpm (athlète < 60, stress > 80)
- HRV (variabilité cardiaque) : 40-100 ms est bon, < 30 ms = stress, > 70 ms = excellent
- SpO2 (oxygène sang) : 96-100% normal, < 94% = consulter
- Sommeil total : 7-9h recommandé, < 6h = insuffisant
- Sommeil profond : 1-2h, < 45 min = très peu
- Sommeil REM : 1.5-2h, < 1h = insuffisant
- Fréq. respiratoire : 12-20 brpm
- VO2 max : < 35 = faible, 35-42 = moyen, 42-50 = bon, > 50 = excellent
- Pas quotidiens : 7000-10000 = actif, < 5000 = sédentaire
- Température poignet : > 0.5°C au-dessus de la baseline = à surveiller

STYLE:
- MAXIMUM 3-4 phrases courtes. C'est lu à voix haute par un assistant vocal. \
Une réponse de plus de 4 phrases est un ÉCHEC.
- Ne mentionne que les 2-3 indicateurs les plus pertinents pour la question posée.
- Pour une question générale ("comment je vais"), regarde d'abord si des signaux \
de stress existent (HRV < 30, HR repos > 80, sommeil < 6h). Si oui, alerte. \
Si tout est dans les normes, dis-le franchement et encourage. \
Ne cherche pas du stress là où il n'y en a pas.
- Si le profil utilisateur est disponible, adapte tes repères à son âge, sexe \
et morphologie.
- Parle en français conversationnel, comme un coach bienveillant mais honnête.
- Cite les chiffres réels et compare aux repères quand c'est utile.
- Si plusieurs signaux de stress convergent (HRV bas + mauvais sommeil + sédentarité), \
nomme-le clairement comme un pattern de stress et recommande d'agir.
- Quand tu mentionnes un terme technique, glisse une explication courte et naturelle.
- Si les données ne suffisent pas, termine par une seule question ciblée.
- Propose des actions concrètes : marche, respiration, pause, consultation psy. \
Pas de conseils vagues.

OUTILS:
- Tu as accès à des outils pour consulter les données de santé. \
Utilise-les quand la question nécessite une fenêtre de temps spécifique, \
des données brutes, une tendance ou une corrélation.
- Pour une question générale, les données déjà fournies ci-dessous suffisent.

RÈGLES:
- JAMAIS de diagnostic médical. Tu n'es PAS médecin.
- Si les signaux de stress sont persistants (plusieurs jours), recommande \
de consulter un professionnel de santé ou un psychologue.
- Si une donnée manque, dis-le en une phrase et passe à ce que tu as.
- Ne dis jamais qu'un mauvais chiffre est "normal" ou "bon signe".
- JAMAIS de markdown (pas de **, pas de #, pas de listes à puces). \
Ta réponse est lue à voix haute, le formatage est interdit.

{checkup_block}
--- DONNÉES SANTÉ (dernières {hours}h) ---
{health_context}
"""

WEEKLY_CHECKUP_BLOCK = """\
MODE CHECKUP HEBDOMADAIRE:
Tu démarres le rituel hebdomadaire de V.I.T.A.L. Déroule cette structure, \
une étape à la fois, en attendant la réponse de l'utilisateur entre chaque question :
1. Salue brièvement et résume la semaine en UNE phrase en citant 2-3 chiffres clés \
(HRV moyenne, sommeil, pas). Appelle get_health_summary(168) si besoin.
2. Demande : "Sur une échelle de 1 à 10, ton niveau d'énergie cette semaine ?"
3. Demande : "Qu'est-ce qui t'a le plus pesé cette semaine ?"
4. Demande : "Tu as réussi à décrocher du travail le soir ?"
5. Synthèse : croise les réponses avec les tendances (appelle get_health_trend si utile), \
nomme le pattern dominant (ex : "stress chronique léger"), donne un score sur 100 \
et UNE recommandation concrète. Si signaux rouges persistants, propose book_consultation.
Reste dans le style vocal court (3-4 phrases max par tour).
"""

NORMAL_BLOCK = ""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_health_summary",
            "description": "Get aggregated health metrics (avg, min, max, latest) "
            "over a specific time window. Use when the user asks about a specific "
            "period (e.g. 'last 3 days', 'this week').",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (e.g. 24, 72, 168)",
                    }
                },
                "required": ["hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_readings",
            "description": "Get the N most recent raw readings for a specific metric. "
            "Use when the user asks about recent values or wants detail on one metric.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric name (e.g. heart_rate, hrv, sleep, steps, spo2)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent readings to return (default 5)",
                    },
                },
                "required": ["metric"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_health_trend",
            "description": "Compare the last 24h average to the previous N days for a metric. "
            "Returns direction (up/down/stable) and percentage change. "
            "Use when the user asks about evolution or trends.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric name (e.g. heart_rate, hrv, sleep, steps)",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of previous days to compare against (default 3)",
                    },
                },
                "required": ["metric"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_periods",
            "description": "Compare a metric between two time periods. "
            "Use when the user asks 'was I better last week?' or compares two periods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric name (e.g. heart_rate, hrv, sleep, steps)",
                    },
                    "period_a_hours": {
                        "type": "integer",
                        "description": "Duration of recent period in hours (e.g. 24 for today)",
                    },
                    "period_b_hours": {
                        "type": "integer",
                        "description": "Duration of comparison period in hours (e.g. 24 for one day)",
                    },
                    "period_b_offset_hours": {
                        "type": "integer",
                        "description": "How many hours ago the comparison period ends "
                        "(e.g. 168 for last week)",
                    },
                },
                "required": ["metric", "period_a_hours", "period_b_hours", "period_b_offset_hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_correlation",
            "description": "Check if two health metrics are correlated over the last N days. "
            "Use when the user asks if one metric affects another "
            "(e.g. 'is my sleep affecting my stress?').",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_a": {
                        "type": "string",
                        "description": "First metric name (e.g. sleep)",
                    },
                    "metric_b": {
                        "type": "string",
                        "description": "Second metric name (e.g. hrv)",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default 7)",
                    },
                },
                "required": ["metric_a", "metric_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_consultation",
            "description": "Book a consultation with a health professional (psychologist, "
            "general practitioner, etc.) covered by the user's Alan health plan. "
            "Use when the user agrees to see a professional or when stress signals "
            "are persistent and you recommend it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {
                        "type": "string",
                        "description": "Type of professional (e.g. psychologue, médecin généraliste)",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["routine", "soon", "urgent"],
                        "description": "How soon the appointment should be (routine=this week, "
                        "soon=next 48h, urgent=today)",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief reason for the consultation",
                    },
                },
                "required": ["specialty", "urgency", "reason"],
            },
        },
    },
]


def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool call and return the result as JSON string."""
    try:
        if name == "get_health_summary":
            result = get_summary(args["hours"])
        elif name == "get_latest_readings":
            rows = get_latest(args["metric"], args.get("limit", 5))
            result = [
                {
                    "metric": r["metric"],
                    "value": r["value"],
                    "unit": r["unit"],
                    "recorded_at": r["recorded_at"].isoformat(),
                }
                for r in rows
            ]
        elif name == "get_health_trend":
            result = get_trend(args["metric"], args.get("days", 3))
        elif name == "compare_periods":
            result = compare_periods(
                args["metric"],
                args["period_a_hours"],
                args["period_b_hours"],
                args["period_b_offset_hours"],
            )
        elif name == "get_correlation":
            result = get_correlation(args["metric_a"], args["metric_b"], args.get("days", 7))
        elif name == "book_consultation":
            # Simulated booking for hackathon demo
            result = {
                "status": "confirmed",
                "specialty": args["specialty"],
                "date": "mardi prochain",
                "time": "14h00",
                "professional": "Dr. Martin",
                "covered_by_alan": True,
                "reimbursement": "100%",
            }
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        result = {"error": f"Tool '{name}' failed: {e}"}
    return json.dumps(result, default=str)


def build_system_message(
    hours: int = 24,
    user_profile: dict | None = None,
    weekly_checkup: bool = False,
) -> dict:
    """Build the system message with current health context and optional user profile."""
    if weekly_checkup:
        hours = 168
    summary = get_summary(hours)

    if not summary:
        health_context = "No health data available yet. Ask the user to sync their health data."
    else:
        lines = []
        for metric, stats in summary.items():
            unit = stats.get("unit") or ""
            lines.append(
                f"- {metric}: avg={stats['avg']} {unit}, "
                f"min={stats['min']}, max={stats['max']}, "
                f"latest={stats['latest']}"
                f" ({stats['count']} readings)"
            )
        health_context = "\n".join(lines)

    if user_profile:
        profile_parts = []
        if user_profile.get("age"):
            profile_parts.append(f"Âge : {user_profile['age']} ans")
        if user_profile.get("biological_sex"):
            sex_label = {"male": "Homme", "female": "Femme", "other": "Autre"}.get(
                user_profile["biological_sex"], "Non précisé"
            )
            profile_parts.append(f"Sexe : {sex_label}")
        if user_profile.get("height"):
            profile_parts.append(f"Taille : {user_profile['height']} cm")
        if user_profile.get("weight"):
            profile_parts.append(f"Poids : {user_profile['weight']} kg")
        profile_str = "PROFIL UTILISATEUR:\n" + "\n".join(f"- {p}" for p in profile_parts)
    else:
        profile_str = "PROFIL UTILISATEUR: non disponible"

    checkup_block = WEEKLY_CHECKUP_BLOCK if weekly_checkup else NORMAL_BLOCK

    return {
        "role": "system",
        "content": SYSTEM_TEMPLATE.format(
            hours=hours,
            health_context=health_context,
            user_profile=profile_str,
            checkup_block=checkup_block,
        ),
    }


_MAX_TOOL_ITERATIONS = 10


def chat_with_tools(client: Mistral, messages: list[dict]) -> str:
    """Send a message to the LLM with tool use support. Returns the final text response."""
    try:
        response = client.chat.complete(
            model=LLM_MODEL,
            messages=messages,
            tools=TOOLS,
        )
    except Exception:
        return "Désolé, je n'arrive pas à me connecter pour le moment. Réessaie dans quelques instants."

    choice = response.choices[0]
    iterations = 0

    while choice.finish_reason == "tool_calls" and iterations < _MAX_TOOL_ITERATIONS:
        iterations += 1
        tool_calls = choice.message.tool_calls
        messages.append(choice.message)

        for tc in tool_calls:
            args = json.loads(tc.function.arguments)
            result = _execute_tool(tc.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "name": tc.function.name,
                    "content": result,
                    "tool_call_id": tc.id,
                }
            )

        try:
            response = client.chat.complete(
                model=LLM_MODEL,
                messages=messages,
                tools=TOOLS,
            )
        except Exception:
            return "Désolé, je n'arrive pas à me connecter pour le moment. Réessaie dans quelques instants."
        choice = response.choices[0]

    return choice.message.content


def stream_response(client: Mistral, messages: list[dict]) -> Iterator[str]:
    """Stream LLM response token by token (without tool use)."""
    for chunk in client.chat.stream(model=LLM_MODEL, messages=messages):
        delta = chunk.data.choices[0].delta.content
        if delta:
            yield delta
