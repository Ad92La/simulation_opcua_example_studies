import asyncio
import os
import sys

# Make the 'src' package directory importable (packages live under src/).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from simulation.production_line import ProductionLine


async def test_simulation():
    line = ProductionLine()

    print("🔧 Initialisiere Produktionslinie...")
    print(f"Maschinen: {len(line.machines)}")
    print(f"Puffer: {len(line.buffers)}")

    # 10 Zyklen testen
    for i in range(10):
        result = await line.run_cycle()
        kpis = line.get_kpi_data()

        print(f"\n📊 Zyklus {i + 1}:")
        print(f"  Produziert: {result['produced']}")
        print(f"  OEE: {kpis['oee']:.1f}%")
        print(f"  Durchsatz: {kpis['throughput']:.1f}/h")

        # Maschinenstatus anzeigen
        machine_status = [(m.name, m.status.name) for m in line.machines]
        print(f"  Maschinen: {machine_status}")

    print(f"\n✅ Test abgeschlossen")
    print(f"Gesamt produziert: {line.total_produced}")


if __name__ == "__main__":
    asyncio.run(test_simulation())