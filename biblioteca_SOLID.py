from abc import ABC, abstractmethod
import datetime

#ITEMS: Define la abstracción general de ítems de biblioteca

class ItemBiblioteca(ABC):
    def __init__(self, id_item: str, titulo: str):
        self.id = id_item
        self.titulo = titulo
        self.disponible = True

    @abstractmethod
    def tipo(self) -> str:
        pass


class Libro(ItemBiblioteca):
    def __init__(self, id_item: str, titulo: str, autor: str):
        super().__init__(id_item, titulo)
        self.autor = autor

    def tipo(self):
        return "Libro"


class Revista(ItemBiblioteca):
    def __init__(self, id_item: str, titulo: str, numero: int):
        super().__init__(id_item, titulo)
        self.numero = numero

    def tipo(self):
        return "Revista"

#Contiene la clase GestorDeInventario que gestiona la colección de 
#ítems: agregar, eliminar, obtener, verificar disponibilidad.
class GestorDeInventario:
    def __init__(self):
        self.items = {}

    def agregar_item(self, item) -> bool:
        if item.id in self.items:
            print(f"Ya existe un item con el ID {item.id}")
            return False
        self.items[item.id] = item
        print(f"{item.tipo()} '{item.titulo}' agregado correctamente.")
        return True

    def eliminar_item(self, id_item: str) -> bool:
        item = self.items.get(id_item)
        if not item:
            print("El item no existe.")
            return False
        if not item.disponible:
            print("No se puede eliminar porque está prestado.")
            return False
        del self.items[id_item]
        print(f"{item.tipo()} con ID {id_item} eliminado.")
        return True

    def obtener_item(self, id_item: str):
        return self.items.get(id_item)

    def mostrar_inventario(self):
        if not self.items:
            print("Inventario vacío.")
            return
        print("Inventario:")
        for item in self.items.values():
            estado = "Disponible" if item.disponible else "Prestado"
            print(f"{item.id} - {item.titulo} - {item.tipo()} - {estado}")

#Define la interfaz INotificador y sus implementaciones como NotificadorEmail y NotificadorSMS
#para enviar notificaciones por distintos canales.

class Notificador(ABC):
    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str) -> None:
        pass


class NotificadorEmail(Notificador):
    def enviar(self, destinatario: str, mensaje: str) -> None:
        print(f"[EMAIL a {destinatario}] {mensaje}")


class NotificadorSMS(Notificador):
    def enviar(self, destinatario: str, mensaje: str) -> None:
        print(f"[SMS a {destinatario}] {mensaje}")


#Contiene IRegistradorEventos (interfaz) y RegistradorArchivo (implementación) 
#para registrar eventos (log) sin acoplarse a un medio específico.

class RegistradorEventos(ABC):
    @abstractmethod
    def registrar(self, mensaje: str) -> None:
        pass


class RegistroEnArchivo(RegistradorEventos):
    def __init__(self, archivo: str = "log_biblioteca.txt"):
        self.archivo = archivo

    def registrar(self, mensaje: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{timestamp}] {mensaje}\n"
        with open(self.archivo, "a", encoding="utf-8") as f:
            f.write(linea)
        print(f"(Registrado en archivo): {mensaje}")


class RegistroEnConsola(RegistradorEventos):
    def registrar(self, mensaje: str) -> None:
        print(f"[LOG] {mensaje}")

#Clase ServicioDePrestamos que gestiona los préstamos y devoluciones de ítems. 
#Usa interfaces para registrar eventos y notificar usuarios.

class ServicioDePrestamos:
    def __init__(self, notificador, registrador):
        self.notificador = notificador
        self.registrador = registrador
        self.prestamos = {}  # id_item: usuario

    def prestar(self, usuario: str, item) -> bool:
        if not item.disponible:
            mensaje = f"{item.tipo()} '{item.titulo}' ya está prestado."
            print(mensaje)
            self.registrador.registrar(f"Fallo en préstamo: {mensaje}")
            return False

        item.disponible = False
        self.prestamos[item.id] = usuario
        mensaje = f"{usuario} ha prestado: {item.titulo}"
        self.notificador.enviar(usuario, f"Has prestado: {item.titulo}")
        self.registrador.registrar(f"Préstamo exitoso: {mensaje}")
        return True

    def devolver(self, usuario: str, item) -> bool:
        if item.id not in self.prestamos:
            mensaje = f"Intento de devolución inválida por {usuario} del item {item.titulo}."
            print("Este item no estaba prestado.")
            self.registrador.registrar(mensaje)
            return False

        item.disponible = True
        self.prestamos.pop(item.id)
        mensaje = f"{usuario} ha devuelto: {item.titulo}"
        self.notificador.enviar(usuario, f"Has devuelto: {item.titulo}")
        self.registrador.registrar(f"Devolución exitosa: {mensaje}")
        return True


#Main

# Crear componentes
inventario = GestorDeInventario()
notificador = NotificadorEmail()
registrador = RegistroEnArchivo()
servicio_prestamos = ServicioDePrestamos(notificador, registrador)

# Crear ítems
libro = Libro("L001", "1984", "George Orwell")
revista = Revista("R001", "Muy Interesante", 203)

# Agregar ítems al inventario
inventario.agregar_item(libro)
inventario.agregar_item(revista)

# Mostrar inventario
inventario.mostrar_inventario()

# Prestar libro
servicio_prestamos.prestar("juan@example.com", libro)

# Intentar prestar de nuevo (debe fallar)
servicio_prestamos.prestar("ana@example.com", libro)

# Mostrar inventario actualizado
inventario.mostrar_inventario()

# Devolver libro
servicio_prestamos.devolver("juan@example.com", libro)

# Mostrar inventario final
inventario.mostrar_inventario()