import asyncio
from asyncua import Client


async def test_connection():
    url = "opc.tcp://localhost:50000"
    try:
        client = Client(url=url)
        await client.connect()
        print("✅ Verbindung erfolgreich!")

        # Root-Node erkunden
        root = client.nodes.root
        objects = await root.get_children()
        print("📁 Root Children:", [await obj.read_browse_name() for obj in objects[:5]])

        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_connection())