import argparse
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from src.simulation.production_line import ProductionLine
from src.opcua_client.client import ProductionOPCUAClient
from src.llm_integration.analyzer import ProductionLLMAnalyzer
from src.llm_integration.optimizer import LLMOptimizer

# ============ LOGGING KONFIGURATION ============
if sys.platform == "win32":
    # Windows: Verwende UTF-8 für die Konsole
    import codecs

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# Logging konfigurieren - OHNE Emojis für Windows-Kompatibilität
class SafeConsoleHandler(logging.StreamHandler):
    """Handler der Unicode-Emojis durch ASCII-Äquivalente ersetzt"""

    # Emoji zu ASCII Mapping
    EMOJI_MAP = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '🚀': '[START]',
        '🛑': '[STOP]',
        '📊': '[DATA]',
        '📦': '[BOX]',
        '📈': '[CHART]',
        '📉': '[CHART]',
        '🔴': '[RED]',
        '🟢': '[GREEN]',
        '🟡': '[YELLOW]',
        '🟠': '[ORANGE]',
        '⚡': '[POWER]',
        '🏗️': '[BUILD]',
        '🗑️': '[TRASH]',
        '💡': '[IDEA]',
        '🤖': '[ROBOT]',
        '📡': '[SIGNAL]',
        '🧹': '[CLEAN]',
        '👋': '[BYE]',
        '🏭': '[FACTORY]',
        '✨': '[STAR]',
        '⚪': '[WHITE]',
        '📐': '[RULER]',
        '📅': '[CAL]',
        '🔄': '[REFRESH]',
        'ℹ️': '[INFO]',
        '🟣': '[PURPLE]',
        '⚙️': '[GEAR]',
        '📣': '[ANNOUNCE]',
        '📝': '[NOTE]',
        '🔧': '[WRENCH]',
        '🔨': '[HAMMER]',
        '📋': '[CLIPBOARD]',
        '📁': '[FOLDER]',
        '📂': '[FOLDER]',
        '📄': '[FILE]',
        '📑': '[DOC]',
    }

    def emit(self, record):
        try:
            msg = self.format(record)
            # Ersetze Emojis
            for emoji, ascii_rep in self.EMOJI_MAP.items():
                msg = msg.replace(emoji, ascii_rep)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log', encoding='utf-8'),
        SafeConsoleHandler()
    ]
)

logger = logging.getLogger(__name__)

# Umgebungsvariablen laden
load_dotenv()


class ProductionSimulation:
    def __init__(self, llm_provider: str = "openai"):
        self.production_line = ProductionLine()
        self.opcua_client = ProductionOPCUAClient(
            server_url=os.getenv("OPCUA_SERVER_URL", "opc.tcp://localhost:50000")
        )

        # LLM Integration
        self.llm_analyzer = None
        self.llm_optimizer = None
        self.llm_provider = llm_provider

        if llm_provider == "mci":
            self._init_mci_llm()
        else:
            self._init_openai_llm()

        self.running = False
        self.llm_interval = int(os.getenv("SIMULATION_CYCLES_PER_LLM", 300))
        self.simulation_speed = float(os.getenv("SIMULATION_SPEED", 0.1))

        # Stats
        self.start_time = None
        self.cycle_times = []

        # Signal Handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _init_openai_llm(self):
        """Default LLM path: OpenAI (unchanged behavior)."""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.llm_analyzer = ProductionLLMAnalyzer(
                    api_key=api_key,
                    model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
                )
                self.llm_optimizer = LLMOptimizer(self.production_line, self.llm_analyzer)
                logger.info("LLM integration enabled (OpenAI)")
            except Exception as e:
                logger.warning(f"LLM initialization failed: {e}")
        else:
            logger.warning("No OpenAI API key found. LLM optimization disabled.")

    def _init_mci_llm(self):
        """MCI LLM path: activated via `--llm mci` (Task 3)."""
        # Imported lazily so the default OpenAI path is unaffected.
        from src.llm_integration.mci_analyzer import MCIProductionAnalyzer

        # Accept both our MCI_* names and the CLIENT_ID/CLIENT_SECRET names
        # used in the MCI example snippet.
        api_key = os.getenv("MCI_API_KEY") or os.getenv("CLIENT_ID")
        api_secret = os.getenv("MCI_API_SECRET") or os.getenv("CLIENT_SECRET")
        if api_key and api_secret:
            try:
                # IMPORTANT: use a dedicated MCI_MODEL (default gpt-4o) so the
                # OpenAI-oriented LLM_MODEL (e.g. gpt-4-turbo-preview) is NOT
                # sent to MCI, which would reject it with HTTP 400.
                self.llm_analyzer = MCIProductionAnalyzer(
                    api_key=api_key,
                    api_secret=api_secret,
                    base_url=os.getenv("MCI_BASE_URL"),
                    model=os.getenv("MCI_MODEL", "gpt-4o"),
                )
                self.llm_optimizer = LLMOptimizer(self.production_line, self.llm_analyzer)
                logger.info("LLM integration enabled (MCI)")
            except Exception as e:
                logger.warning(f"MCI LLM initialization failed: {e}")
        else:
            logger.warning(
                "No MCI credentials (MCI_API_KEY/MCI_API_SECRET). "
                "LLM optimization disabled."
            )

    def _signal_handler(self, sig, frame):
        """Signal-Handler für sauberes Beenden"""
        logger.info("🛑 Received shutdown signal")
        self.running = False

    async def start(self):
        """Startet die Simulation"""
        logger.info("Starting Production Line Simulation")
        self.start_time = datetime.now()

        # OPC-UA verbinden
        try:
            await self.opcua_client.connect()
        except Exception as e:
            logger.error(f"Failed to connect to OPC-UA: {e}")
            logger.info("Starting without OPC-UA connection...")

        self.running = True

        # Status-Reporting Timer
        last_status_report = 0
        status_interval = 100

        # Hauptsimulationsloop
        while self.running:
            try:
                # Performance-Timing
                cycle_start = datetime.now()

                # Produktionszyklus ausführen
                cycle_result = await self.production_line.run_cycle()

                # Zykluszeit tracken
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                self.cycle_times.append(cycle_duration)
                if len(self.cycle_times) > 1000:
                    self.cycle_times = self.cycle_times[-1000:]

                # OPC-UA aktualisieren
                if self.opcua_client.connected:
                    await self.opcua_client.update_all(self.production_line)

                # LLM-Optimierung (nur alle N Zyklen)
                if (self.llm_optimizer and
                        self.production_line.cycle_count % self.llm_interval == 0 and
                        self.production_line.cycle_count > 0):
                    logger.info("Running LLM optimization cycle...")
                    optimization_result = await self.llm_optimizer.optimize_cycle()

                    if optimization_result:
                        self._log_optimization(optimization_result)

                # Status loggen
                if self.production_line.cycle_count % status_interval == 0:
                    self._log_status()

                # Detaillierter Zustand alle 10 Zyklen (Terminal-Ausgabe)
                if self.production_line.cycle_count % 10 == 0:
                    self._log_detailed_state()

                # Zyklus-Timing anpassen
                actual_sleep = max(0, self.simulation_speed - cycle_duration)
                await asyncio.sleep(actual_sleep)

            except Exception as e:
                logger.error(f"Simulation error: {e}", exc_info=True)
                await asyncio.sleep(1)

        await self.cleanup()

    def _log_status(self):
        """Loggt den aktuellen Status"""
        kpis = self.production_line.get_kpi_data()
        flow = self.production_line.get_production_flow()

        avg_cycle = sum(self.cycle_times[-100:]) / len(self.cycle_times[-100:]) if self.cycle_times else 0

        logger.info(
            f"Cycle {self.production_line.cycle_count} | "
            f"OEE: {kpis['oee']:.1f}% | "
            f"Throughput: {kpis['throughput']:.1f}/h | "
            f"Produced: {kpis['total_produced']} | "
            f"Scrap: {kpis['scrap_rate']:.1f}% | "
            f"Avg Cycle: {avg_cycle:.3f}s"
        )

        # Maschinenstatus
        for machine in self.production_line.machines:
            logger.debug(f"  {machine.name}: {machine.status.name} | "
                         f"OEE: {machine.oee_component['oee']:.1f}% | "
                         f"Quality: {machine.metrics.quality_rate:.1f}%")

    def _log_detailed_state(self):
        """Gibt alle 10 Zyklen eine detaillierte Übersicht der Maschinen, Puffer und Lager auf die Konsole aus."""
        try:
            cycle = self.production_line.cycle_count
            logger.info("""
================ DETAILED STATE =================
""")

            # Maschinen
            logger.info(f"Machines (cycle={cycle}):")
            for m in self.production_line.machines:
                progress = 0.0
                try:
                    progress = (1.0 - (m.current_cycle_remaining / m.cycle_time)) if m.cycle_time > 0 and m.status.name == 'RUNNING' else 0.0
                except Exception:
                    progress = 0.0
                logger.info(
                    f"  - {m.name}: status={m.status.name}, produced={m.metrics.total_produced}, "
                    f"quality={m.metrics.quality_rate:.1f}%, oee={m.oee_component['oee']:.3f}, "
                    f"progress={progress*100:.0f}% ({m.current_cycle_remaining:.2f}s remaining)"
                )

            # Puffer
            logger.info("Buffers:")
            for b in self.production_line.buffers:
                logger.info(
                    f"  - {b.name}: fill={b.fill_level:.1f}% ({len(b.products)}/{b.capacity}), "
                    f"overflow={b.overflow_count}, starvation={b.starvation_count}, throughput={b.total_through}"
                )

            # Lager
            input_wh = self.production_line.input_warehouse
            recycling = self.production_line.recycling_warehouse
            finished = self.production_line.finished_goods
            logger.info("Warehouses:")
            logger.info(
                f"  - {input_wh.name}: stock={input_wh.stock_level}/{input_wh.capacity} "
                f"({input_wh.utilization:.1f}% full)"
            )
            logger.info(
                f"  - {recycling.name}: stock={recycling.stock_level}/{recycling.capacity} "
                f"({recycling.utilization:.1f}% full)"
            )
            logger.info(
                f"  - {finished.name}: stock={finished.stock_level}/{finished.capacity} "
                f"({finished.utilization:.1f}% full)"
            )

            logger.info("===============================================")
        except Exception as e:
            logger.debug(f"Failed to log detailed state: {e}")

    def _log_optimization(self, result: dict):
        """Loggt Optimierungsergebnisse"""
        analysis = result.get("analysis", {})
        applied = result.get("applied", [])

        if analysis:
            logger.info(f"Bottleneck: {analysis.get('bottleneck', 'N/A')}")
            logger.info(f"Critical Issue: {analysis.get('critical_issue', 'N/A')}")

            improvements = analysis.get("top_improvements", [])
            for imp in improvements:
                logger.info(f"  💡 {imp.get('priority')}. {imp.get('action')} "
                            f"(Expected OEE gain: {imp.get('expected_oee_gain', 0):.1f}%)")

        if applied:
            for opt in applied:
                logger.info(f"Applied: {opt}")

    async def cleanup(self):
        """Aufräumen beim Beenden"""
        logger.info("🧹 Cleaning up...")

        if self.opcua_client.connected:
            await self.opcua_client.disconnect()

        # Zusammenfassung ausgeben
        kpis = self.production_line.get_kpi_data()
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        logger.info("=" * 60)
        logger.info("SIMULATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Runtime: {runtime:.1f} seconds")
        logger.info(f"Total cycles: {self.production_line.cycle_count}")
        logger.info(f"Total produced: {kpis['total_produced']}")
        logger.info(f"Total scrap: {kpis['total_scrap']}")
        logger.info(f"Average OEE: {kpis['oee']:.1f}%")
        logger.info(f"Scrap rate: {kpis['scrap_rate']:.1f}%")
        logger.info(f"Throughput: {kpis['throughput']:.1f} Stk/h")

        # Maschinen-Zusammenfassung
        logger.info("\n🤖 Machine Summary:")
        for machine in self.production_line.machines:
            logger.info(f"  {machine.name}: "
                        f"Produced={machine.metrics.total_produced}, "
                        f"OEE={machine.oee_component['oee']:.1f}%, "
                        f"Quality={machine.metrics.quality_rate:.1f}%, "
                        f"Errors={machine.metrics.errors_count}")

        # Puffer-Zusammenfassung
        logger.info("\n📦 Buffer Summary:")
        for buffer in self.production_line.buffers:
            logger.info(f"  {buffer.name}: "
                        f"Fill={buffer.fill_level:.1f}%, "
                        f"Overflow={buffer.overflow_count}, "
                        f"Starvation={buffer.starvation_count}")

        # Lager-Zusammenfassung
        logger.info("\n🏭 Warehouse Summary:")
        logger.info(f"  {self.production_line.input_warehouse.name}: "
                    f"Stock={self.production_line.input_warehouse.stock_level}")
        logger.info(f"  {self.production_line.recycling_warehouse.name}: "
                    f"Stock={self.production_line.recycling_warehouse.stock_level}")
        logger.info(f"  {self.production_line.finished_goods.name}: "
                    f"Stock={self.production_line.finished_goods.stock_level}")

        logger.info("=" * 60)


async def main(llm_provider: str = "openai"):
    """Hauptfunktion"""
    simulation = ProductionSimulation(llm_provider=llm_provider)
    await simulation.start()


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Production line simulation with optional LLM optimization."
    )
    parser.add_argument(
        "--llm",
        choices=["openai", "mci"],
        default="openai",
        help="LLM provider for optimization suggestions. "
             "'openai' (default) uses OPENAI_API_KEY; "
             "'mci' uses the MCI REST API (MCI_API_KEY/MCI_API_SECRET).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        asyncio.run(main(args.llm))
    except KeyboardInterrupt:
        logger.info("👋 Simulation stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)