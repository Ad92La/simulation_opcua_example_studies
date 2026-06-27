import asyncio
import os
from dotenv import load_dotenv
from simulation.production_line import ProductionLine
from llm_integration.analyzer import ProductionLLMAnalyzer
from llm_integration.optimizer import LLMOptimizer

load_dotenv()


async def test_optimization():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Kein API-Key gefunden")
        return

    line = ProductionLine()
    analyzer = ProductionLLMAnalyzer(api_key)
    optimizer = LLMOptimizer(line, analyzer)

    # Baseline: vor der Optimierung
    print("📊 Baseline-Daten:")
    kpis_before = line.get_kpi_data()
    print(f"  OEE: {kpis_before['oee']:.1f}%")
    print(f"  Durchsatz: {kpis_before['throughput']:.1f}/h")

    # Simulation laufen lassen
    print("\n⚙️ Simulation läuft...")
    for i in range(10):
        await line.run_cycle()

    # Optimierung
    print("\n🤖 Starte Optimierung...")
    result = await optimizer.optimize_cycle()

    if result:
        print("\n✅ Optimierung abgeschlossen")
        print(f"  Angewandte Änderungen: {len(result.get('applied', []))}")

        # Nach der Optimierung
        kpis_after = line.get_kpi_data()
        print(f"\n📊 Nach Optimierung:")
        print(f"  OEE: {kpis_after['oee']:.1f}%")
        print(f"  Durchsatz: {kpis_after['throughput']:.1f}/h")

        oee_change = kpis_after['oee'] - kpis_before['oee']
        print(f"  OEE-Veränderung: {oee_change:+.1f}%")
    else:
        print("❌ Optimierung fehlgeschlagen")


if __name__ == "__main__":
    asyncio.run(test_optimization())