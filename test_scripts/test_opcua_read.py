import asyncio
from asyncua import Client


async def test_read():
    url = "opc.tcp://localhost:50000"
    client = Client(url=url)
    await client.connect()

    # Versuche alle möglichen Node-Pfade
    test_nodes = [
        "ns=3;s=ProductionLine_Machines_Fraese1_Status",
        "ns=3;s=ProductionLine_Machines_Fraese1_Counter",
        "ns=3;s=ProductionLine_KPIs_OEE",
        "ns=3;s=ProductionLine_Buffers_Buffer1_Level"
    ]

    for node_path in test_nodes:
        try:
            node = client.get_node(node_path)
            value = await node.read_value()
            print(f"✅ {node_path}: {value}")
        except Exception as e:
            print(f"❌ {node_path}: {e}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_read())