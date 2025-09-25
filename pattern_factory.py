from jobs import Packet
import json

class PedidoFactory:
    @staticmethod
    def crear_pedido(data):
        return Packet.from_dict(data)
    

with open("cache/jobs.json", "r", encoding="utf-8") as f:
    data = json.load(f)




