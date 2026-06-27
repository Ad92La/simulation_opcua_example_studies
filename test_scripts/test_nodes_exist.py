import asyncio
import json
from asyncua import Client

async def test_nodes():
    url = "opc.tcp://localhost:50000"

    async with Client(url=url) as client:

        with open("../docker/opc-plc/init-nodes.json", "r") as f:
            config = json.load(f)

        print(f"Teste {len(config['NodeList'])} Nodes...\n")

        for node_info in config["NodeList"]:
            node_id = f"ns=3;s={node_info['NodeId']}"

            print(f"Teste Node: {node_id}")

            try:
                node = client.get_node(node_id)

                browse_name = await node.read_browse_name()
                value = await node.read_value()

                print(f"  ✅ Existiert")
                print(f"     BrowseName: {browse_name}")
                print(f"     Value: {value}")

            except Exception as e:
                print(f"  ❌ Fehler: {e}")

            print()
if __name__ == "__main__":
    asyncio.run(test_nodes())