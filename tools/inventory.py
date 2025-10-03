from collections import deque

# Inventario de paquetes (pedidos) del jugador
class Inventory:
    def __init__(self, max_weight):
        self.max_weight = max_weight
        self.items = deque()   # lista doblemente enlazada de pedidos aceptados

    def total_weight(self):
        return sum(p.weight for p in self.items)

    def can_accept(self, packet) -> bool:
        return self.total_weight() + packet.weight <= self.max_weight

    def add(self, packet) -> bool:
        if self.can_accept(packet):
            self.items.append(packet)  # agregar al final
            return True
        return False

    def remove(self, packet):
        try:
            self.items.remove(packet)
        except ValueError:
            pass  # no estaba en la lista

    def remove_by_id(self, packet_id: str):
        """Elimina un pedido del inventario usando su ID"""
        for p in list(self.items):  # hacemos copia para evitar errores
            if str(p.id) == str(packet_id):
                self.items.remove(p)
                return True
        return False

    def clear_all(self):
        """Vacía por completo el inventario"""
        self.items.clear()

    def view_by_priority(self):
        return sorted(self.items, key=lambda p: p.priority, reverse=True)

    def view_by_deadline(self):
        return sorted(self.items, key=lambda p: p.deadline)

    def forward(self):
        """Recorre de inicio a fin"""
        for item in self.items:
            yield item

    def backward(self):
        """Recorre de fin a inicio"""
        for item in reversed(self.items):
            yield item