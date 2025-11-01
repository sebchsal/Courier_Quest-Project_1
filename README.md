<img src="images\Courier_Quest.png"> 

## <img src="images\gif.gif" width ="25"><b> Acerca del proyecto:</b>
Courier Quest es un proyecto de estructuras de datos para videojuegos desarrollado en Python utilizando Pygame como biblioteca principal para su desarrollo. El juego se basa en simular a un repartidor que debe aceptar y completar pedidos en una ciudad, donde debe gestionar los tiempos de entrega, los cambios meteorológicos que afectarán a sus rutas, el inventario y qué entregas son prioritarias.

## <img src="images\Data.gif" width ="25"><b> Estructuras de Datos y Complejidad Algorítmica:</b>

El proyecto utiliza varias estructuras de datos eficientes para manejar el estado del juego y sus componentes:

- **Cola doble (`deque`)** → para el inventario del jugador y la cola de puntuaciones.
- **Listas y diccionarios** → para manejar los datos del mapa, puntajes y partidas guardadas.
- **Composición de objetos (POO)** → para modelar entidades como el jugador, el clima, el mapa y la cámara.

| Componente | Estructura | Complejidad | Descripción |
|-------------|-------------|--------------|--------------|
| Inventario | `deque` | `O(1)` inserción / eliminación, `O(n)` ordenamiento | Manejo eficiente de pedidos aceptados |
| Cola de puntajes | `deque` | `O(1)` | FIFO para registro de nombres |
| Datos del juego | `list`, `dict` | `O(n log n)` | Almacenamiento y ordenamiento de puntajes |
| Renderizado | `list` | `O(n)` | Dibujo de mapa y objetos por frame |
| Cámara | Escalares | `O(1)` | Cálculo de desplazamiento |
| Bucle principal | — | `O(n)` | Actualización por cada ciclo de juego |

**Complejidad promedio por frame:** `O(n)`  
(*n = cantidad de objetos activos en pantalla*)

## <img src="images\Computer_Gif.gif" width ="25"><b> Lenguajes de programación y bibliotecas utilizados:</b>

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40px" style="margin: 10px;" />
  <img src="images\pygame_logo.png" width="85px" style="margin: 40px;" />
</div>
Instalar pygame con:

```bash
pip install pygame
```

## <img src="images\Tools_Gif.gif" width ="25"><b> Herramientas de Software & IDE's:</b>

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" width="40px" style="margin: 10px;" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" width="40px" style="margin: 10px;" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" width="40px" style="margin: 10px;" />
</div>

## <img src="images\Pixel_Coding_M.gif" width ="45"><b> Desarollado por:</b> <img src="images\Pixel_Coding_W.gif" width ="45">
* Priscilla Murillo Romero
* Sebastián Chaves Salazar
