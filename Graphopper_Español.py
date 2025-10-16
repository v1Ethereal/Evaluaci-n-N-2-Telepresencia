import requests
import urllib.parse

# URL base y clave de API de GraphHopper
route_url = "https://graphhopper.com/api/1/route?"
key = "a4e0fa61-126f-4249-bc8a-9a177475a304"  # Reemplazar con API propia

# ------------------------------------------------------------
# FUNCIÓN PARA GEOCODIFICAR UNA DIRECCIÓN
# ------------------------------------------------------------
def geocoding(location, key):
    while location.strip() == "":
        location = input("Por favor, ingresa nuevamente la ubicación: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    respuesta = requests.get(url)
    datos = respuesta.json()
    estado = respuesta.status_code

    if estado == 200 and len(datos["hits"]) != 0:
        lat = datos["hits"][0]["point"]["lat"]
        lng = datos["hits"][0]["point"]["lng"]
        nombre = datos["hits"][0]["name"]
        valor = datos["hits"][0]["osm_value"]

        pais = datos["hits"][0].get("country", "")
        estado_ubic = datos["hits"][0].get("state", "")

        if estado_ubic and pais:
            nueva_loc = f"{nombre}, {estado_ubic}, {pais}"
        elif estado_ubic:
            nueva_loc = f"{nombre}, {estado_ubic}"
        elif pais:
            nueva_loc = f"{nombre}, {pais}"
        else:
            nueva_loc = nombre

        print(f"Ubicación encontrada: {nueva_loc} (Tipo: {valor})\n{url}")
    else:
        lat = None
        lng = None
        nueva_loc = location
        if estado != 200:
            print(f"Error {estado}: {datos.get('message', 'No se recibió respuesta del servidor.')}")
    return estado, lat, lng, nueva_loc

# ------------------------------------------------------------
# FUNCIÓN PARA CALCULAR Y MOSTRAR LA RUTA
# ------------------------------------------------------------
def calcular_ruta(origen, destino, vehiculo, key):
    route_url = "https://graphhopper.com/api/1/route?"
    parametros = {
        "point": [f"{origen[1]},{origen[2]}", f"{destino[1]},{destino[2]}"],
        "vehicle": vehiculo,
        "locale": "es",  # idioma español para instrucciones
        "key": key,
        "points_encoded": "false"
    }

    url = route_url + urllib.parse.urlencode(parametros, doseq=True)
    respuesta = requests.get(url)
    datos = respuesta.json()

    if respuesta.status_code == 200 and "paths" in datos:
        ruta = datos["paths"][0]
        distancia = ruta["distance"] / 1000  # en km
        tiempo = ruta["time"] / 60000        # en minutos

        print("\n================ RESULTADOS DEL VIAJE ================")
        print(f"Distancia total: {distancia:.2f} km")
        print(f"Tiempo estimado: {tiempo:.2f} minutos\n")

        print("Instrucciones paso a paso:")
        for i, instruccion in enumerate(ruta["instructions"], start=1):
            print(f"{i}. {instruccion['text']} ({instruccion['distance'] / 1000:.2f} km)")

        print("=======================================================\n")

    else:
        print(f"\nNo se pudo calcular la ruta. Error: {respuesta.status_code}")
        print(datos.get("message", "No se recibió respuesta válida de la API."))

# ------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------
while True:
    print("\n=============================================")
    print("Perfiles de transporte disponibles en Graphhopper:")
    print("=============================================")
    print("auto   bicicleta   a pie\n")

    vehiculo_usuario = input("Elige un medio de transporte (o escribe 's' / 'salir' para salir): ").lower().strip()
    if vehiculo_usuario in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    # Traducción al formato de la API
    if vehiculo_usuario in ["auto", "coche", "carro"]:
        vehiculo = "car"
    elif vehiculo_usuario in ["bicicleta", "bici"]:
        vehiculo = "bike"
    elif vehiculo_usuario in ["a pie", "caminar", "pie"]:
        vehiculo = "foot"
    else:
        print("No se ingresó un medio de transporte válido. Se usará 'auto' por defecto.")
        vehiculo = "car"

    loc1 = input("Ubicación de origen: ").strip()
    if loc1.lower() in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    estado1, lat1, lng1, origen = geocoding(loc1, key)
    if lat1 is None:
        print("No se pudo obtener la ubicación de origen.")
        continue

    loc2 = input("Ubicación de destino: ").strip()
    if loc2.lower() in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    estado2, lat2, lng2, destino = geocoding(loc2, key)
    if lat2 is None:
        print("No se pudo obtener la ubicación de destino.")
        continue

    calcular_ruta((estado1, lat1, lng1, origen), (estado2, lat2, lng2, destino), vehiculo, key)
