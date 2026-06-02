# Plan de Implementación Frontend (MVP)

Este documento establece la hoja de ruta y la estructura sugerida para el desarrollo del frontend del e-commerce, conectándose directamente a la API desarrollada en FastAPI.

## 1. Visión General y Alcance
El objetivo es construir una interfaz de usuario escalable, rápida y modular que consuma los endpoints expuestos por el backend de e-commerce. Este plan se centra en el Producto Mínimo Viable (MVP) basado en las historias de usuario críticas:
- Navegación y catálogo de productos (con categorías).
- Gestión del carrito de compras.
- Proceso de checkout y generación de pedidos (Orders & Bills).
- Perfil del cliente, direcciones y reseñas.

## 2. Stack Tecnológico Sugerido
*(Pendiente de confirmación. Si tenés otra preferencia, lo adaptamos al toque).*
- **Framework Core**: React 18+ (Next.js recomendado para SEO y Server-Side Rendering) o Vue 3 (Nuxt).
- **Estilos**: Tailwind CSS (para prototipado rápido y consistente).
- **Gestión de Estado**: Zustand (React) o Pinia (Vue) para el estado global (Carrito, Usuario).
- **Cliente HTTP y Caché**: Axios + React Query (o TanStack Query) para manejar paginación, reintentos y caché sincronizada con el backend.
- **Tipado**: TypeScript estricto, basándose en los esquemas Pydantic del backend (`ClientSchema`, `ProductSchema`, etc.).

## 3. Arquitectura del Frontend
La estructura del proyecto debe reflejar la modularidad del backend:

```text
src/
├── api/          # Configuración de Axios, interceptores (para manejar tokens/errores)
├── components/   # UI atómica: Botones, Modales, Tarjetas de Producto
├── features/     # Módulos de negocio (Cart, Checkout, Profile, Catalog)
├── hooks/        # Lógica reutilizable (ej: useCart, useProducts)
├── pages/        # Vistas enrutables (Home, Product Detail, Checkout)
├── services/     # Funciones que llaman a la API (ProductService, OrderService)
└── types/        # Interfaces TypeScript (mapeadas 1 a 1 con Pydantic)
```

## 4. Fases de Desarrollo (MVP)

### Fase 1: Configuración Core y Enrutamiento
- [ ] Inicializar el proyecto con el stack elegido.
- [ ] Configurar cliente HTTP (Axios) apuntando a `http://localhost:8000`.
- [ ] Implementar interceptores globales para manejar errores 400/404/500 (alineados con los errores del backend).
- [ ] Configurar layout base (Header, Footer, Navegación).

### Fase 2: Catálogo y Búsqueda (Read-Only)
- [ ] **Servicios**: `GET /products` (con `skip`/`limit`) y `GET /categories`.
- [ ] **Vistas**: Home Page, Listado de Categorías, Grilla de Productos.
- [ ] **Componentes**: `ProductCard` (muestra nombre, precio, stock) y `Pagination`.
- [ ] **Detalle**: Vista individual llamando a `GET /products/{id}` (incluyendo reseñas).

### Fase 3: Gestión de Carrito y Estado Local
- [ ] **Estado**: Implementar store global para el carrito (Zustand/Redux).
- [ ] **Funciones**: Agregar/Quitar ítems, validación **local** de stock máximo disponible antes de enviar al backend.
- [ ] **Vistas**: Modal lateral de carrito (Drawer) o vista completa de "Revisar Carrito".

### Fase 4: Clientes y Direcciones (Usuarios)
- [ ] **Servicios**: `POST /clients`, `GET /clients/{id}`, `POST /addresses`.
- [ ] **Vistas**: Registro de usuario, Login (si aplica), Mi Perfil.
- [ ] **Formularios**: Formularios con validación en el cliente (ej: `react-hook-form` + `zod`) asegurando que los datos cumplan con los regex del backend (ej: teléfono).

### Fase 5: Proceso de Checkout (Escritura Crítica)
*Esta es la parte más sensible del negocio.*
- [ ] **Flujo de Usuario**: Selección de dirección de envío -> Resumen de pedido -> Confirmación.
- [ ] **Llamadas Secuenciales / Transaccionales**:
  1. Validar que el `Client` y `Address` existan.
  2. Crear la factura (`POST /bills`).
  3. Crear la orden (`POST /orders` pasando `client_id` y `bill_id`).
  4. Generar iterativamente (o en lote si la API lo soporta) los `POST /order_details`.
- [ ] **Manejo de Errores**: Atrapar 409 o 422 si hay falta de stock (validado por `OrderDetailService` en el backend) y mostrar feedback amigable.

### Fase 6: Historial, Reseñas y Monitoreo
- [ ] **Historial**: Vista "Mis Pedidos" (consultando `GET /orders` filtrado por cliente).
- [ ] **Reseñas**: Formulario para dejar `POST /reviews` en productos comprados.
- [ ] **Salud (Opcional/Admin)**: Dashboard básico que consuma `GET /health_check` para ver latencia y estado de Redis/DB.

## 5. Mapeo de Endpoints a Componentes (Referencia)

| Funcionalidad Frontend | Endpoint Backend (FastAPI) | Método | Comentarios |
| ---------------------- | -------------------------- | ------ | ----------- |
| Catálogo de Productos  | `/products`                | GET    | Usa caché Redis de 5 min. |
| Menú de Categorías     | `/categories`              | GET    | Usa caché Redis de 1 hora. |
| Detalle de Producto    | `/products/{id}`           | GET    | |
| Perfil del Cliente     | `/clients/{id}`            | GET/PUT| |
| Direcciones de Envío   | `/addresses`               | POST   | |
| Generación de Factura  | `/bills`                   | POST   | Requisito para generar Order. |
| Generación de Orden    | `/orders`                  | POST   | |
| Detalle de Items       | `/order_details`           | POST   | Acá ocurre el descuento de stock. |
| Alta de Reseñas        | `/reviews`                 | POST   | |

---
**Siguiente Paso:** Definir formalmente el framework (¿React o Vue?), armar el repositorio y arrancar con la Fase 1.
