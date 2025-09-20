from abc import ABC, abstractmethod
import datetime

#ITEMS: Define la abstracción general de ítems de biblioteca
class ItemBiblioteca(ABC):
    def __init__(self, id_item, titulo):
        self.id_item = id_item
        self.titulo = titulo
        self.disponible = True

    @abstractmethod
    def tipo(self):
        pass

class Libro(ItemBiblioteca):
    def tipo(self):
        return "Libro"

class Revista(ItemBiblioteca):
    def tipo(self):
        return "Revista"

#Contiene la clase GestorDeInventario que gestiona la colección de 
#ítems: agregar, eliminar, obtener, verificar disponibilidad.
class GestorDeInventario:
    def __init__(self):
        self.items = {}

    def agregar_item(self, item):
        if item.id_item not in self.items:
            self.items[item.id_item] = item
            print(f"{item.tipo()} '{item.titulo}' agregado al inventario.")
        else:
            print(f"El item con ID {item.id_item} ya existe.")

    def eliminar_item(self, id_item):
        if id_item in self.items:
            del self.items[id_item]
            print(f"Item con ID {id_item} eliminado.")
        else:
            print(f"Item con ID {id_item} no encontrado.")

    def obtener_item(self, id_item):
        return self.items.get(id_item)

    def esta_disponible(self, id_item):
        item = self.obtener_item(id_item)
        return item and item.disponible

#Define la interfaz INotificador y sus implementaciones como NotificadorEmail y NotificadorSMS
#para enviar notificaciones por distintos canales.

class INotificador(ABC):
    @abstractmethod
    def enviar(self, destinatario, mensaje):
        pass


class NotificadorEmail(INotificador):
    def enviar(self, destinatario, mensaje):
        print(f"Email enviado a {destinatario}: {mensaje}")


class NotificadorSMS(INotificador):
    def enviar(self, destinatario, mensaje):
        print(f"SMS enviado a {destinatario}: {mensaje}")


#Contiene IRegistradorEventos (interfaz) y RegistradorArchivo (implementación) 
#para registrar eventos (log) sin acoplarse a un medio específico.

class IRegistradorEventos(ABC):
    @abstractmethod
    def registrar(self, evento):
        pass


class RegistradorArchivo(IRegistradorEventos):
    def registrar(self, evento):
        with open("log_biblioteca.txt", "a") as f:
            f.write(f"[{datetime.datetime.now()}] {evento}\n")
        print("Evento registrado en archivo.")

#Clase ServicioDePrestamos que gestiona los préstamos y devoluciones de ítems. 
#Usa interfaces para registrar eventos y notificar usuarios.

class ServicioDePrestamos:
    def __init__(self, inventario, notificador: INotificador, registrador: IRegistradorEventos):
        self.inventario = inventario
        self.notificador = notificador
        self.registrador = registrador
        self.prestamos = {}

    def prestar_item(self, id_item, usuario):
        item = self.inventario.obtener_item(id_item)
        if item and item.disponible:
            item.disponible = False
            self.prestamos[id_item] = usuario
            mensaje = f"{usuario} ha prestado el {item.tipo()} '{item.titulo}'"
            self.registrador.registrar(f"Préstamo: {mensaje}")
            self.notificador.enviar(usuario, "Has prestado un ítem.")
            print(f"{item.tipo()} prestado a {usuario}.")
        else:
            print("El ítem no está disponible o no existe.")

    def devolver_item(self, id_item):
        if id_item in self.prestamos:
            usuario = self.prestamos.pop(id_item)
            item = self.inventario.obtener_item(id_item)
            item.disponible = True
            mensaje = f"{usuario} ha devuelto el {item.tipo()} '{item.titulo}'"
            self.registrador.registrar(f"Devolución: {mensaje}")
            print(f"{item.tipo()} devuelto por {usuario}.")
        else:
            print("Este ítem no estaba prestado.")

#Clase (Biblioteca) que coordina todas las operaciones: delega las tareas a las clases correspondientes.
#No tiene lógica propia.

class Biblioteca:
    def __init__(self, gestor_inventario, servicio_prestamos):
        self.inventario = gestor_inventario
        self.prestamos = servicio_prestamos

    def agregar_item(self, item):
        self.inventario.agregar_item(item)

    def eliminar_item(self, id_item):
        self.inventario.eliminar_item(id_item)

    def prestar_item(self, id_item, usuario):
        self.prestamos.prestar_item(id_item, usuario)

    def devolver_item(self, id_item):
        self.prestamos.devolver_item(id_item)

#Main

Crear componentes
inventario = GestorDeInventario()
notificador = NotificadorEmail()
registrador = RegistradorArchivo()
servicio_prestamos = ServicioDePrestamos(inventario, notificador, registrador)
biblioteca = Biblioteca(inventario, servicio_prestamos)

# Agregar ítems
libro1 = Libro("L001", "1984")
revista1 = Revista("R001", "National Geographic")

biblioteca.agregar_item(libro1)
biblioteca.agregar_item(revista1)

# Prestar y devolver
biblioteca.prestar_item("L001", "alice@example.com")
biblioteca.devolver_item("L001")
