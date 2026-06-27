from simulation.buffers import Buffer, Product


def test_buffer():
    buffer = Buffer("TestBuffer", 3)

    # Produkte hinzufügen
    for i in range(5):
        product = Product(f"P_{i}", "test")
        success = buffer.add_product(product)
        print(f"Füge P_{i} hinzu: {'✅' if success else '❌ Buffer voll'}")

    print(f"Füllstand: {buffer.fill_level:.0f}%")
    print(f"Anzahl: {len(buffer.products)}")

    # Produkte entfernen
    for i in range(4):
        product = buffer.remove_product()
        print(f"Entferne: {product.id if product else '❌ Buffer leer'}")

    print(f"Überläufe: {buffer.overflow_count}")
    print(f"Hunger: {buffer.starvation_count}")


if __name__ == "__main__":
    test_buffer()