import asyncio
import os
import sys

# Make the 'src' package directory importable (packages live under src/).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dotenv import load_dotenv
from llm_integration.analyzer import ProductionLLMAnalyzer
from simulation.production_line import ProductionLine

load_dotenv()


async def test_analyzer():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Kein API-Key gefunden")
        return

    analyzer = ProductionLLMAnalyzer(api_key)
    line = ProductionLine()

    # Simulation ein paar Zyklen laufen lassen
    for i in range(5):
        await line.run_cycle()

    # Daten sammeln
    sim_data = {
        "machines": line.get_machine_data(),
        "buffers": line.get_buffer_data(),
        "kpis": line.get_kpi_data(),
        "raw_stock": line.raw_material.stock_level,
        "finished_stock": line.finished_goods.stock_level,
        "simulation_time": line.simulation_time
    }

    print("🤖 Starte LLM-Analyse...")
    result = await analyzer.analyze(sim_data)

    if result:
        print("\n📊 Analyse-Ergebnis:")
        print(f"  OEE: {result.get('analysis', {}).get('overall_oee', 'N/A')}")
        print(f"  Bottleneck: {result.get('analysis', {}).get('bottleneck', 'N/A')}")

        improvements = result.get('top_improvements', [])
        print(f"\n💡 Top {len(improvements)} Verbesserungen:")
        for imp in improvements:
            print(f"  {imp.get('priority')}: {imp.get('action')}")
    else:
        print("❌ Analyse fehlgeschlagen")


if __name__ == "__main__":
    asyncio.run(test_analyzer())