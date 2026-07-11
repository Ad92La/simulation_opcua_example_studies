"""
Optimierte Prompts für das LLM mit Fokus auf Token-Effizienz
"""

SYSTEM_PROMPT = """Du bist ein Experte für Produktionsoptimierung und Lean Manufacturing.
Analysiere Produktionsdaten präzise und gib konkrete, umsetzbare Verbesserungsvorschläge.
Fokussiere auf die größten Hebel zur Effizienzsteigerung.
Antworte ausschließlich im JSON-Format."""

PRODUCTION_ANALYSIS_PROMPT = """
Analysiere diese Produktionsdaten und identifiziere die TOP 3 Verbesserungsmaßnahmen:

{production_data}

Antworte mit diesem JSON:
{{
    "analysis": {{
        "overall_oee": <zahl>,
        "bottleneck": "<maschinenname>",
        "critical_issue": "<beschreibung in max 50 chars>",
        "efficiency_score": <1-10>
    }},
    "top_improvements": [
        {{
            "priority": <1-3>,
            "action": "<konkrete aktion in max 80 chars>",
            "target": "<maschine/puffer>",
            "expected_oee_gain": <prozentpunkte>,
            "implementation_effort": "<low|medium|high>"
        }}
    ],
    "parameter_suggestions": {{
        "machine_adjustments": [
            {{
                "machine": "<name>",
                "parameter": "<taktzeit|fehlerrate>",
                "current_value": <wert>,
                "suggested_value": <wert>,
                "reasoning": "<kurze begründung>"
            }}
        ],
        "buffer_adjustments": [
            {{
                "buffer": "<name>",
                "current_capacity": <wert>,
                "suggested_capacity": <wert>
            }}
        ]
    }}
}}

Wichtig: Maximal 3 Improvements, fokussiere auf höchsten Impact bei geringstem Aufwand.
"""

PRODUCTION_DATA_TEMPLATE = """
Maschinen (Status, Takt[s], Fehlerrate, Produziert, OEE[%]):
{machines}

Puffer (Füllstand[%], Kapazität, Überläufe):
{buffers}

Lager:
- Rohmaterial: {raw_stock}
- Fertigwaren: {finished_stock}

KPIs:
- OEE: {oee:.1f}%
- Durchsatz: {throughput:.1f} Stk/h
- Ausschuss: {scrap:.1f}%
- Auslastung: {utilization:.1f}%
"""

# Prompt für die Validierung von Änderungen
VALIDATION_PROMPT = """
Validiere ob diese Optimierungsvorschläge technisch sinnvoll sind:

Vorschläge:
{suggestions}

Aktuelle Konfiguration:
{current_config}

Bewerte mit:
{{
    "valid_suggestions": [<indizes der validen vorschläge>],
    "risks": ["<mögliche risiken>"],
    "estimated_real_oee_gain": <konservative schätzung in %>
}}
"""