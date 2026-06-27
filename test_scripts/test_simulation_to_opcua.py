import asyncio
from simulation.production_line import ProductionLine
from opcua_client.client import ProductionOPCUAClient


async def test_integration():
    # Simulation starten
    global machine_data
    line = ProductionLine()
    client = ProductionOPCUAClient()

    try:
        await client.connect()
        print("✅ OPC-UA verbunden")

        # 5 Zyklen laufen lassen und Daten updaten
        for i in range(5):
            await line.run_cycle()

            # Daten sammeln
            machine_data = line.get_machine_data()
            buffer_data = line.get_buffer_data()
            kpi_data = line.get_kpi_data()

            # An OPC-UA senden
            await client.update_machine_data(machine_data)
            await client.update_buffer_data(buffer_data)
            await client.update_kpi_data(kpi_data)

            print(f"✅ Zyklus {i + 1}: Daten an OPC-UA gesendet")

        # Vorher/nachher Vergleich
        print("\n📊 Letzte Maschinendaten:")
        for machine in machine_data:
            print(f"  {machine['name']}: Status={machine['status']}, OEE={machine['oee']:.1f}%")

    except Exception as e:
        print(f"❌ Fehler: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_integration())