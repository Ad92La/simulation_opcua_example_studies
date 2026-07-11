import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import openai
from .prompts import (
    SYSTEM_PROMPT,
    PRODUCTION_ANALYSIS_PROMPT,
    PRODUCTION_DATA_TEMPLATE,
    VALIDATION_PROMPT
)

logger = logging.getLogger(__name__)


class ProductionLLMAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.analysis_history: List[Dict] = []
        self.last_analysis_time: Optional[datetime] = None
        self.min_analysis_interval = 60  # Sekunden zwischen LLM-Aufrufen

    def should_analyze(self, simulation_time: float) -> bool:
        """Prüft ob eine neue Analyse sinnvoll ist"""
        if self.last_analysis_time is None:
            return True

        time_since_last = (datetime.now() - self.last_analysis_time).total_seconds()
        return time_since_last >= self.min_analysis_interval

    def format_production_data(self, simulation_data: Dict) -> str:
        """Formatiert Produktionsdaten für das LLM - optimiert für Token-Effizienz"""
        # Maschinen kompakt formatieren
        machines_str = "\n".join([
            f"- {m['name']}: {m['status']}, Takt={m['cycle_time']}s, "
            f"Fehler={m['error_rate'] * 100:.1f}%, Produziert={m['produced']}, "
            f"OEE={m['oee']:.1f}%"
            for m in simulation_data['machines']
        ])

        # Puffer kompakt formatieren
        buffers_str = "\n".join([
            f"- {b['name']}: Füllstand={b['fill_level']:.0f}%, "
            f"Kap={b['capacity']}, Überlauf={b['overflow']}"
            for b in simulation_data['buffers']
        ])

        # KPIs formatieren
        kpis = simulation_data['kpis']

        return PRODUCTION_DATA_TEMPLATE.format(
            machines=machines_str,
            buffers=buffers_str,
            raw_stock=simulation_data['raw_stock'],
            finished_stock=simulation_data['finished_stock'],
            oee=kpis['oee'],
            throughput=kpis['throughput'],
            scrap=kpis['scrap_rate'],
            utilization=kpis['utilization']
        )

    async def analyze(self, simulation_data: Dict) -> Optional[Dict]:
        """
        Führt eine LLM-Analyse durch - nur wenn genügend neue Daten vorhanden
        """
        if not self.should_analyze(simulation_data.get('simulation_time', 0)):
            logger.debug("Skipping LLM analysis - too soon")
            return None

        try:
            # Daten formatieren
            formatted_data = self.format_production_data(simulation_data)

            # Prompt zusammenstellen
            prompt = PRODUCTION_ANALYSIS_PROMPT.format(
                production_data=formatted_data
            )

            # LLM aufrufen
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )

            # Antwort parsen
            analysis = json.loads(response.choices[0].message.content)

            # Historie aktualisieren
            self.analysis_history.append({
                "timestamp": datetime.now().isoformat(),
                "simulation_time": simulation_data.get('simulation_time', 0),
                "analysis": analysis,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            })

            self.last_analysis_time = datetime.now()

            # Token-Verbrauch loggen
            if hasattr(response, 'usage'):
                logger.info(f"LLM Analysis complete. Tokens used: {response.usage.total_tokens}")

            return analysis

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return None

    def get_latest_suggestions(self) -> Optional[List[Dict]]:
        """Holt die letzten Verbesserungsvorschläge"""
        if self.analysis_history:
            latest = self.analysis_history[-1]
            return latest.get("analysis", {}).get("top_improvements", [])
        return None

    def get_parameter_suggestions(self) -> Optional[Dict]:
        """Holt Parametersvorschläge"""
        if self.analysis_history:
            latest = self.analysis_history[-1]
            return latest.get("analysis", {}).get("parameter_suggestions", {})
        return None