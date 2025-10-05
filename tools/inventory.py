from collections import deque

# Inventario de paquetes (pedidos) del jugador
class Inventory:
    def __init__(self, max_weight):
        self.max_weight = max_weight
        self.items = deque()   # lista doblemente enlazada de pedidos aceptados
    
    # Obtener el peso total de los pedidos en el inventario
    def total_weight(self):
        return sum(p.weight for p in self.items)
    
    # Ver si se puede aceptar un nuevo pedido
    def can_accept(self, packet) -> bool:
        return self.total_weight() + packet.weight <= self.max_weight
    
    # Agregar un pedido al inventario
    def add(self, packet) -> bool:
        if self.can_accept(packet):
            self.items.append(packet)  # agregar al final
            return True
        return False
    
    # Eliminar un pedido del inventario
    def remove(self, packet):
        try:
            self.items.remove(packet)
        except ValueError:
            pass  # no estaba en la lista
    
    # Eliminar un pedido del inventario usando su ID
    def remove_by_id(self, packet_id: str):
        for p in list(self.items):  # hacemos copia para evitar errores
            if str(p.id) == str(packet_id):
                self.items.remove(p)
                return True
        return False

    # limpia
    def clear_all(self):
        self.items.clear()

    # vista por prioridad
    def view_by_priority(self):
        return sorted(self.items, key=lambda p: p.priority, reverse=True)

    # vista por deadline
    def view_by_deadline(self):
        return sorted(self.items, key=lambda p: p.deadline)

    # hacia adelante
    def forward(self):
        for item in self.items:
            yield item

    # hacia atras
    def backward(self):
        for item in reversed(self.items):
            yield item