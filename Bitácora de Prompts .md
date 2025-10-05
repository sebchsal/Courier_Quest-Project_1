**II Ciclo 2025 EIF-207**	  
**Estructuras de Datos**   
**Primer	Proyecto Programado**   
**Courier Quest**

**Integrantes**:

* Priscilla Murillo Romero  
* Sebastián Chaves Salazar

# Bitácora de Prompts 

Mediante el uso de la IA (GPT, Deepseek, ClaudeAI, Gemini) como asistente del proyecto, esta bitácora cuenta con todos los prompts utilizados para la realización del mismo, esto con el fin de mostrar la transparencia en la ayuda solicitada a estas herramientas y las modificaciones realizadas en cada parte del código escrito. 

## Lista de prompts

A continuación se encuentra dividido por categorías de uso y solicitud, los prompts implementados para la funcionalidad en el proyecto:

### Para conexiones con la API:

* “Eres un experto en el desarrollo de juegos, tu tarea es darme una explicación completa sobre la librería Pygame, el uso de cada función, etc. Esto con la intención de lograr desarrollar juegos y aprender de ello. Dame las fuentes y documentaciones necesarias para aprender a usar la librería al completo.”(GPT)  
* "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/docs\#/" “Utilzando la como base la API del link y los archivos adjuntos, dame y realiza los siguiente: Usar los GET's y ante un fallo del API, cargar archivos locales equivalentes de la siguiente forma: \- /data/ciudad.json, \- /data/pedidos.json,  \- /data/weather.json Se debe de guardar copias cacheadas de respuestas en en un directorio /api\_cache con fecha/hora. Es decir, si no hay conexión al API server, se utiliza la última versión.” (Se adjuntó en el chat los archivos del proyecto)(GPT).

### Para establecer uso con imágenes y renderizado de Mapa:

* “Realiza la siguiente modificacion, guiandote con los archivos main.py y player.py, utilzando las imaganes adjuntadas, cuando se usen las teclas indicadas en la clase MovimientoFlechas estas haga la utilizacionde su respectiva imagen, es decir, cuando se presiona la tecla K\_a o K\_LEFT se ponga la imagen delivery\_left.png.” (Se adjuntó en el chat los archivos del proyecto)(GPT).  
* "Haz que el mapa sea más grande para simular una ciudad amplia y que el movimiento siempre se centre en el player usando la imagen (Delivery.png). La cámara debe moverse junto con el jugador hasta los límites del mapa, sin dejar espacios en blanco ni cortes visibles. No debe ser un mapa fijo, pero sí debe mantenerse completo al desplazarse." (GPT)  
* “Dime cómo puedo hacer que la imagen de building pueda abarcar todo el espacio de su ubicación, guíate con los archivos, este cuenta con transparencia de fondo, si hay de redimensionar la imagen building, dime como y los datos de altura y ancho.” No dio el resultado esperado y se usó el siguiente prompt: “Por que la imagen no abarca todo el cuadro”. (ClaudeAI)  
* "Dame la guía para dejar el cambio de que solo se muestre una imagen de (building.png) en el mapa para las casillas que son building" (Se adjuntó en el chat los archivos del proyecto)(GPT).

### Para desarrollo de lógica de Clima:

* “Guiandote con los archivos .py y .json, dame una guia para realizar lo siguiente: Con respecto a la lógica para el cambio climático, ¿cómo realizo un burst que dure entre 45 y 60 segundos de tiempo de juego (Juego debe durar 10–15 minutos de tiempo real)? Al terminar ese tiempo, se debe elegir la siguiente condición climática. Condiciones soportadas y multiplicadores base de velocidad (para la bicicleta):   
  \- clear:	×1.00  
   \- clouds: ×0.98   
  \- rain\_light: ×0.90   
  \- rain:	×0.85   
  \- storm: ×0.75   
  \- fog: ×0.88   
  \- wind:	×0.92   
  \- heat:	×0.90   
  \- cold:	×0.92” (Se adjuntó en el chat los archivos del proyecto)(GPT).  
* “Ahora utilizando la cadena de Markov, define una matriz de transición donde cada fila representa la probabilidad de pasar de un estado climático al siguiente. Ejemplo simple (sólo con 3 climas: despejado, nublado, lluvia) Condición actual Despejado Nublado Lluvia Despejado 0.6 0.3 0.1 Nublado 0.3 0.5 0.2 Lluvia 0.2 0.4 0.4 Es decir, si el clima actual es nublado, hay un	30% de que vuelva a despejarse, un 50% de que siga nublado y un 20% de que cambie a lluvia.”(GPT).

### Para desarrollo de lógica de Entregas, Pedidos y Movimiento:

* “Guiandote con los archivos .py y .json, dame una guia para realizar lo siguiente: Los pedidos serán de dos clases: normales (0) o con prioridad (n) – a mayor el número, mayor prioridad. El jugador puede aceptar o rechazar pedidos conforme avanza el juego, pero solo puede cargar una cantidad máxima de peso. Los pedidos aceptados se almacenan en el inventario (utiliza un TDA) que puede recorrer hacia adelante o hacia atrás para decidir el orden de entrega.Sin embargo, el inventario podrá tener opciones de visualizar los encargos con mayor prioridad u ordenarlos por hora de entrega.”(Se adjuntó en el chat los archivos del proyecto)(GPT). Se utilizó una lista doblemente enlazada para el uso del inventario de player, utilizamos la librería “deque”.  
* “Ahora tomando esto en cuenta y guiandote con todos los archivos, en cuanto a la resistencia del repartidor (player), dame una guia para realizar los siguiente puntos, tomando en cuenta el cambio climático y el peso de los paquetes que se acepten: § Barra	0–100 (inicia en 100). Umbral de recuperación para moverse: 30\. § Estados: Normal (\>30),	Cansado (10–30, velocidad	×0.8), Exhausto (≤0, no se mueve). § Consumo por celda: \-0.5 (base) \+ extras: § Peso total \> 3: \-0.2 por celda por cada unidad sobre 3\. § Clima adverso (rain/wind): \-0.1 por celda; storm: \-0.3 por celda; heat: \-0.2 por celda. § Recuperación parada: \+5 por segundo (puntos de descanso opcionales: \+10/seg).”(GPT). Para desarrollo de los Menús (ventanas):  
* “Dame una guia para poner un background rectangular blanco debajo de las letras las letra del HUD en la ventana” (Se adjuntó en el chat los archivos del proyecto) (Deepseek). Se modificó el HUD (Heads-Up Display o Pantalla de Visualización Frontal) para mostrarlo en el juego junto con background blanco.

### Para desarrollo de la Reputación:

* “Guiandote con los archivos .py y .json, dame una guia para relizar lo siguiente para el juego; El player debe de comenzar en 70/100 y sube o baja según la puntualidad y las acciones del jugador. La reputación se maneja 70\. Derrota inmediata si \<20. Excelencia (≥90): \+5%	pago y se deben de realizar lo siguientes cambios comunes: \- Entrega a tiempo: \+3 \- Entrega temprana	(≥20%	antes): \+5 \- Tarde	≤30s: \-2; 31–120s: \-5; \>120s: \-10 \- Cancelar pedido aceptado: \-4 \- Perder/expirar paquete: \-6 \- Racha de 3 entregas	sin penalización: \+2 (una vez por racha) \- Efectos: multiplicador de pago (+5% si ≥90),	primera tardanza	del día a mitad de penalización si la	reputación ≥85.” (Se adjuntó en el chat los archivos del proyecto)(GPT).  
* “Dame la guia para que el HUD cambie de color, verde si ≥90, amarillo si 50–89, rojo si \<20”(Se adjuntó en el chat los archivos del proyecto) (Deepseek).

### Para desarrollo del Tiempo de entrega:

* “Utilizando los archivos .py, dame una guia para realizar lo siguiente: Haz que el tiempo de entrega se base con el tiempo real del juego no con el deadline, es decir cuando este inicie, cada pedido que se acepte, tiene un tiempo de entrega de 30 segundos, a partir de ahí basate en lo siguientes cambios comunes: Entrega a	tiempo: \+3 o Entrega	temprana (≥20% antes): \+5 o Tarde ≤30s: \-2; 31–120s: \-5; \>120s:	\-10 o Cancelar pedido aceptado: \-4 o Perder/expirar paquete: \-6 o Racha de 3  entregas sin penalización:	\+2 (una vez por racha) o Efectos: multiplicador de pago (+5% si ≥90), primera	tardanza del día a mitad de penalización si la reputación ≥ 85.” (GPT)  
* “Se realizo un bucle infinito cuando se entregan los paquetes, corrige eso guiándote con los archivos .py.” (Se adjuntó en el chat los archivos del proyecto)(GPT). Se corrigió un error que no elimina el pedido entregado de activos, ni los marcados como completados.

### Para desarrollo de la Velocidad y movimiento:

* “Dame un guía para realizar lo siguiente en cuanto a la velocidad y movimiento del player en el juego. El player se presente de la siguiente manera v0 (player) \= 3 celdas/seg (ajustable), utilizando la formula v \= v0 \* Mclima \* Mpeso \* Mrep \* Mresistencia \* surface\_weight(tile) (surface\_weight	proviene de la	leyenda del mapa (ej.: parque 0.95) ). Realiza los parches y no elimines ni agregues demás en el código” (Se adjuntó en el chat los archivos del proyecto)(GPT). La corrección realizada fue corregir la no respuesta del player, este no se movía de la forma correcta, ya que al principio establecimos el movimiento sin tomar en cuenta la fórmula brindada en el enunciado del proyecto.

### Para desarrollo de los Menús (Ventanas):

A partir de los métodos y las guías brindada por los prompts para el desarrollo de las ventanas de “game over” y de “victoria” se continuó con la misma lógica para crear las demás ventanas y menús.

* “Guiandote con el archivo .py y las imagenes .png, dame la guia para en el menu de "Game Over" poner la imagenes en el boton de exit la imagen "btnexit.png", en el boton de play again la imagen "playagain.png" y la imagen de "gameover.png" como el logo del menu” (Se adjuntó en el chat los archivos del proyecto)(GPT).  
* “Crea el la ventana de victoria igual que el de game over, al darle click a btnplayagain.png, se el juego se reinicia y si se da clik a btnexit.png se regresa el menu de inicio” (Se adjuntó en el chat los archivos del proyecto)(GPT).   
* “Corrige el error, cuando se gana el score va disminuyendo de 2 en 2 no debe de pasar eso, cuanta las bonificacion por entrega pero hagas que se dismunya en el menu, al ganar se muestra el menu gameover, se debe de mostrar de de victoria, tambien corrige que si se pierde el exit de game tambien me dirije al menu de inicio” (Se adjuntó en el chat los archivos del proyecto)(GPT). Se corrigió una disminución que se realizaba en el score al ganar o perder una partida.  
* “Reliza lo siguiente, en el menu de inicio agrega el btnhowplay.png en la esquina inferior izquierda, al darle click este abre una pequeña vetana con el logohowplay.png donde explica como jugar el juego, debe de tener lo siguiente: KEYS TO PLAY \[W/UP\]: go up \[A/LEFT\]: go left \[S/DOWN\]: go down \[D/RIGHT\]: go right \[E\]: accept a package \[I\]: open inventory INFO: Orders can be sorted and canceled from the inventory. To deliver it, look for the red symbol on the map and stand on top of it. Pon el btnexit.png para salir de la ventana y volver al menú de inicio” (Se adjuntó en el chat los archivos del proyecto)(GPT).

### Para desarrollo del guardado y cargado del juego:

* “Dame una guia detallada para Implementar un sistema de guardado y puntuaciones donde: en el menú de pausa, al hacer clic en btnsave.png se guarde la partida como archivo binario y redirija al menú principal; en el menú principal, coloca btnload.png a la izquierda de btnnewgame.png para cargar la última partida guardada, btnscore.png a la derecha para mostrar una ventana modal con btnscorelist.png y una tabla del Top 10 (posición, nombre, puntuación), y modifica btnnewgame.png para que abra una ventana modal con logoname.png solicitando el nombre del jugador antes de iniciar; los scores se guardan en formato JSON usando score\_queue.py cuando finaliza el tiempo de juego.” (Se adjuntó en el chat los archivos del proyecto)(GPT).  Se creó un TDA tipo cola para el guardado de los puntajes de cada partido jugado, con el prompt obtuvimos una guia para realizar el guardado y cargado correctamente, utilizando tanto el uso de la imágenes y de los menús.

## Lista de prompts para creacion de imagenes

A continuación se encuentran los prompts utilizados para la creación de la imagenes implementados en los menús y el propio juego:

### Imagen del personaje:

* “Crea una imagen de un repartidor en bicicleta, en estilo pixelart para un video juego, hazlo con fondo blanco, que el repartidor tenga camisa y un casco rojo, hazlo viendo hacia su perfil derecho.” (GPT)  
* “Ahora hazlo viendo dirección hacia arriba” (Se adjunto la imagen del repartidor para crearlo con las diferentes direcciones) (GPT)  
* “Hazlo viendo hacia el norte, es decir, despaladas” (GPT)  
* “Ahora hazlo haciendo viendo hacia el sur, es decir, de frente” (GPT)

### Imágenes de los edificios y parques:

* Crea una imagen de un edificio moderno el cual estas viendo de frente, en estilo pixelart para un video juego, hazlo con fondo blanco, haz que dentro del edificio,  no debe de verse lo que hay dentro, solamente una silueta ya que predominan más las ventanas, debe ser rectangular, ancho y alto  
* “Crea una imagen rectangular de arbustos que estén rodeados de un muro de cemento con verjas de metal, hazlo en estilo de pixelart para un videojuego. La imagen debe ser grande y que sus límites (muros y vallas) lleguen justo hasta los bordes del lienzo de la imagen, de modo que no haya espacio.” (GPT)

### Imágenes de los botones:

* “Crea la imagen de un botón de "Play Again" en estilo pixelart para un video juego, debe tener forma rectangular ovalado, de color amarillo y con fondo blanco” (Gemini)  
* “Crea la imagen de un botón de "Exit" en estilo pixelart para un video juego, debe tener forma rectangular ovalado, de color rojo y con fondo blanco” (Gemini)  
* “Crea la imagen de un botón de "Play Game" en estilo pixelart para un video juego, debe tener forma rectangular ovalado, de color amarillo y con fondo blanco” (Gemini)  
* “Crea la imagen de un botón de "Score List" en estilo pixelart para un video juego, debe tener forma rectangular ovalado, de color amarillo y con fondo blanco” (Gemini)  
* “Crea la imagen de un botón de "Exit Game" en estilo pixelart para un video juego, debe tener forma rectangular ovalado, de color rojo y con fondo blanco” (Gemini)  
* “crea una imagen que diga "Clear Inventory" de color morado, con la misma figura y con el fondo en color negro” (Gemini)  
* “Ahora crea una imagen que diga "Delete Package" de color rojo, con la misma figura y con el fondo en color negro” (Gemini)  
* “crea una imagen que diga "Sort by Priority" de color verde, con la misma figura y con el fondo en color negro” (Gemini)  
* “Ahora crea una imagen que diga "Sort by Deadline" de color azul, con la misma figura y con el fondo en color negro” (Gemini)  
* “crea una imagen que diga "New Game" de color amarillo, con la misma figura y con el fondo en color negro” (Gemini)  
* “Ahora crea una imagen que diga "Load Game" de color amarillo, con la misma figura y con el fondo en color negro” (Gemini)  
* “Ahora crea una imagen que diga "Save Game and Exit" de color amarillo, con la misma figura y con el fondo en color negro” (Gemini)  
* “Ahora crea una imagen que diga "Resume" de color amarillo, con la misma figura y con el fondo en color negro” (Gemini) 

### Imágenes de los logos y símbolos:

* “Ahora crea una imagen de un logo con el nombre de "Courier Quest Tiger City", hazlo en estilo pixelart para un videojuego, las letras "Courier Quest" deben ser amarillas y la palabra de "Tiger City" de tener en su fondo la piel de un tigre de bengala y estar debajo de "Courier Quest", el logo debe estar sobre un fondo blanco” (Gemini)  
* “Ahora crea una imagen de letras que diga "Inventory" de color amarillo, en estilo pixelart con el fondo en color blanco” (Gemini)  
* “Ahora crea una imagen de letras que diga "Game Over" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "Pause" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de los signos (los palos) de pausa de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "By Pri & Sebas" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "You Won" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "Score List" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "Enter a name" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen de letras que diga "How to play" de color blanco, en estilo pixelart con el fondo en color gris” (Gemini)  
* “Ahora crea una imagen que diga "How to play" de color amarillo, con la misma figura y con el fondo en color negro” (Gemini)  
  