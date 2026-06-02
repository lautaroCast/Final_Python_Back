import os
import sys

# Añadir el directorio actual al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import SessionLocal
from models.category import CategoryModel
from models.product import ProductModel
from models.client import ClientModel

def seed_database():
    print("Iniciando el semillero (seeder)...")
    db = SessionLocal()
    
    try:
        # 1. Verificar si ya hay datos para no duplicar
        if db.query(CategoryModel).first():
            print("La base de datos ya tiene categorías. Saltando el seeder.")
            return

        print("1. Creando categorías...")
        categories_data = [
            {"name": "electronics"},
            {"name": "home"},
            {"name": "fashion"},
            {"name": "sports"},
            {"name": "books"},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat = CategoryModel(name=cat_data["name"])
            db.add(cat)
            categories.append(cat)
            
        db.commit()
        for cat in categories:
            db.refresh(cat)
            
        # Mapear nombres de categorías a IDs
        cat_map = {cat.name: cat.id_key for cat in categories}

        print("2. Creando productos...")
        products_data = [
            {
                "name": "Auriculares Noise Cancelling ZX",
                "description": "Audio inmersivo con cancelación activa de ruido y batería de 30 horas.",
                "price": 159999.0,
                "stock": 50,
                "category_id": cat_map["electronics"]
            },
            {
                "name": "Lámpara Nórdica Minimal",
                "description": "Ilumina tus espacios con un toque moderno y acogedor.",
                "price": 45999.0,
                "stock": 200,
                "category_id": cat_map["home"]
            },
            {
                "name": "Mochila Urbana 25L",
                "description": "Resistente al agua, perfecta para llevar tu notebook y apuntes.",
                "price": 68999.0,
                "stock": 100,
                "category_id": cat_map["fashion"]
            },
            {
                "name": "Set Mancuernas Ajustables",
                "description": "Para entrenar en casa con el peso que necesites.",
                "price": 129999.0,
                "stock": 30,
                "category_id": cat_map["sports"]
            },
            {
                "name": "Kindle Paper Reader",
                "description": "Lleva toda tu biblioteca con vos en un dispositivo liviano.",
                "price": 98999.0,
                "stock": 75,
                "category_id": cat_map["books"]
            },
            {
                "name": "Teclado Mecánico Pro",
                "description": "Switches mecánicos para una experiencia de tipeo inigualable.",
                "price": 87999.0,
                "stock": 40,
                "category_id": cat_map["electronics"]
            },
            {
                "name": "Alfombra Yoga Comfort",
                "description": "Grosor ideal para amortiguar tus articulaciones en cada postura.",
                "price": 31999.0,
                "stock": 150,
                "category_id": cat_map["sports"]
            },
            {
                "name": "Set Organizadores Cocina",
                "description": "Mantené tu alacena impecable con este juego de recipientes herméticos.",
                "price": 27999.0,
                "stock": 80,
                "category_id": cat_map["home"]
            }
        ]

        for p_data in products_data:
            product = ProductModel(**p_data)
            db.add(product)
            
        print("3. Creando usuarios/clientes de prueba...")
        clients_data = [
            {
                "name": "Admin",
                "lastname": "Test",
                "email": "admin@finalfront.com",
                "telephone": "+541111111111"
            },
            {
                "name": "User",
                "lastname": "Test",
                "email": "user@finalfront.com",
                "telephone": "+542222222222"
            }
        ]
        
        for c_data in clients_data:
            client = ClientModel(**c_data)
            db.add(client)

        db.commit()
        print("¡Base de datos populada con éxito!")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
