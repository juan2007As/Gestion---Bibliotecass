# Script para insertar 30 libros de prueba en la base de datos
from Proyecto import Libro
import sqlite3
import random

titulos = [
    "Cien años de soledad", "El amor en los tiempos del cólera", "Don Quijote de la Mancha", "1984", "Orgullo y prejuicio",
    "El señor de los anillos", "Crónica de una muerte anunciada", "Rayuela", "Fahrenheit 451", "Matar a un ruiseñor",
    "La sombra del viento", "El principito", "La casa de los espíritus", "Los miserables", "Drácula",
    "El retrato de Dorian Gray", "El alquimista", "It", "El código Da Vinci", "La ladrona de libros",
    "El nombre de la rosa", "El perfume", "La tregua", "Pedro Páramo", "Ensayo sobre la ceguera",
    "El túnel", "La ciudad y los perros", "El viejo y el mar", "Rebelión en la granja", "Crimen y castigo"
]
autores = [
    "Gabriel García Márquez", "Miguel de Cervantes", "George Orwell", "Jane Austen", "J.R.R. Tolkien",
    "Julio Cortázar", "Ray Bradbury", "Harper Lee", "Carlos Ruiz Zafón", "Antoine de Saint-Exupéry",
    "Isabel Allende", "Victor Hugo", "Bram Stoker", "Oscar Wilde", "Paulo Coelho",
    "Stephen King", "Dan Brown", "Markus Zusak", "Umberto Eco", "Patrick Süskind",
    "Mario Benedetti", "Juan Rulfo", "José Saramago", "Ernesto Sabato", "Mario Vargas Llosa",
    "Ernest Hemingway", "Aldous Huxley", "Fiódor Dostoyevski"
]
generos = [
    "Realismo mágico", "Novela", "Clásico", "Distopía", "Romance", "Fantasía", "Drama", "Ciencia ficción", "Aventura", "Misterio"
]
editoriales = [
    "Sudamericana", "Planeta", "Alfaguara", "Secker & Warburg", "T. Egerton", "Allen & Unwin", "Debolsillo", "Vintage", "Anagrama", "Destino"
]

def insertar_libros_prueba():
    # Eliminar todos los libros existentes directamente en la base de datos
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Libro')
    conn.commit()
    conn.close()
    # Insertar exactamente 30 libros de prueba
    for i in range(30):
        libro = Libro(
            id_libro=i+1,
            titulo=titulos[i % len(titulos)],
            autor=autores[i % len(autores)],
            editorial=editoriales[i % len(editoriales)],
            año=random.randint(1900, 2022),
            genero=generos[i % len(generos)],
            imagen=None
        )
        libro.guardar()
    print("Base de datos 'Libro' limpiada e insertados exactamente 30 libros de prueba.")

if __name__ == "__main__":
    insertar_libros_prueba()
