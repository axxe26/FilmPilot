# Filmpilot

Aplicación web Django para gestionar películas, series y anime, registrar lo que ya viste, guardar favoritos y watchlist, calificar contenido y recibir recomendaciones personalizadas usando la API de TMDB.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Django](https://img.shields.io/badge/Django-6.x-green) ![Django REST Framework](https://img.shields.io/badge/DRF-3.x-orange) ![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

## 1. Encabezado
- Nombre del proyecto: Filmpilot
- Descripción: rastreador personal de películas, series y anime con favoritos, watchlist, ratings, recomendaciones y estadísticas personales, usando la API de TMDB.
- Badges: Python, Django, Django REST Framework, SQLite

## 2. Descripción general
Filmpilot es una app enfocada en ayudar a los usuarios a organizar y seguir su consumo de contenido audiovisual. Permite registrar qué películas y series han visto, marcar episodios y temporadas, guardar contenido para ver después, calificar lo que ya consumieron y consultar recomendaciones basadas en su historial.

La aplicación consume datos de The Movie Database (TMDB) para mostrar información de películas, series y anime, además de trailers, reparto, proveedores de streaming y contenido similar. La autenticación de usuarios se realiza con el sistema de autenticación integrado de Django.

## 3. Funcionalidades
- Registro, login y logout de usuarios: disponibles desde la landing page y el dashboard mediante formularios de autenticación.
- Dashboard con secciones Home, My Content, Recommendations y Statistics: acceso desde la barra lateral de la interfaz.
- Búsqueda de películas, series y anime: la sección Home incluye búsqueda global combinada y filtros por género, popularidad, fecha de estreno y próximos estrenos.
- Búsqueda global combinada: el buscador superior consulta un endpoint de búsqueda global y muestra resultados de películas, series y anime.
- Detalle de película/serie: la vista de detalles muestra póster, backdrop, rating, fecha, géneros, proveedores, tráiler, reparto y contenido similar.
- Marcar como visto: permite marcar películas, temporadas completas y episodios individuales como vistos.
- Sistema de calificación: cada contenido puede recibir una calificación de 1 a 5 estrellas.
- Watchlist: permite guardar elementos para ver más tarde desde la vista de detalle.
- Favoritos: permite guardar elementos como favoritos desde la vista de detalle.
- Actividad reciente en el dashboard: muestra acciones recientes como películas vistas, favoritos y watchlist; incluye acción de “Clear History”.
- Recomendaciones personalizadas: se generan con base en favoritos, ratings y contenido completado del usuario.
- Gráficos de estadísticas: el dashboard muestra gráficos de géneros más vistos y estado del contenido (watching/completed/planned/dropped).
- Perfil de usuario: permite editar nombre, apellido, email, username, foto de perfil, “about me” y cambiar contraseña.

## 4. Tecnologías usadas
- Backend: Django + Django REST Framework
- Base de datos: SQLite (configurada en settings.py para desarrollo)
- Frontend: HTML, CSS y JavaScript vanilla, con Chart.js para gráficos
- API externa: TMDB (The Movie Database)
- Librerías adicionales: requests, pandas, numpy, scikit-learn, Pillow

## 5. Requisitos previos
- Python 3.10 o superior
- pip
- Una cuenta gratuita en https://www.themoviedb.org/ para obtener una API key
- Git (opcional, si vas a clonar el repositorio)

## 6. Instalación paso a paso
Sigue estos pasos desde la raíz del proyecto.

1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd finalproject
```

2. Crear y activar un entorno virtual

Windows (PowerShell):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (cmd):
```cmd
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar dependencias
Este proyecto incluye un archivo requirements.txt preparado para instalar las dependencias necesarias.
```bash
pip install -r requirements.txt
```

4. Crear un archivo .env
El proyecto ya trae una API key fija en settings.py, pero lo recomendable para desarrollo es definir las variables de entorno de forma explícita. Crea un archivo .env en la raíz del proyecto con contenido similar a este:

```env
TMDB_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_aqui
```

> Nota: en este repositorio actual, settings.py está usando una API key directa y un SECRET_KEY hardcodeado, por lo que la aplicación puede correr sin .env, aunque se recomienda mover esas configuraciones a variables de entorno para desarrollo más limpio.

5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crear un superusuario
```bash
python manage.py createsuperuser
```

7. Ejecutar el servidor
```bash
python manage.py runserver
```

8. Abrir la app
Abre tu navegador en:
```text
http://127.0.0.1:8000/
```

## 7. Variables de entorno

| Variable | Para qué sirve | Dónde conseguirla | Obligatoria |
|---|---|---|---|
| TMDB_API_KEY | Permite consumir la API de TMDB para obtener datos de películas, series, trailers, proveedores y contenido similar | https://www.themoviedb.org/ | Sí |
| SECRET_KEY | Clave secreta usada por Django para firmar sesiones y seguridad básica | Se genera localmente o se puede usar una cadena aleatoria | Sí para entornos seguros |

## 8. Estructura del proyecto
```text
finalproject/
├── app/                  # Lógica principal de la app: modelos, vistas, URLs y recomendaciones
│   ├── models.py         # Modelos de perfil, contenido del usuario, watchlist, favoritos y ratings
│   ├── views.py          # Vistas para autenticación, dashboard, detalles y acciones de contenido
│   ├── urls.py           # Rutas de la aplicación
│   └── recommendations.py  # Generación de recomendaciones personalizadas
├── finalproject/         # Configuración principal del proyecto Django
│   ├── settings.py       # Configuración de apps, base de datos, estáticos, API y secret key
│   └── urls.py           # URLs globales del proyecto
├── templates/            # Plantillas HTML para home, dashboard y detalles
├── static/               # Archivos CSS, JavaScript e imágenes
├── media/                # Archivos subidos por los usuarios (fotos de perfil)
├── db.sqlite3            # Base de datos SQLite local
├── manage.py             # Punto de entrada de Django
└── requirements.txt      # Dependencias del proyecto
```

## 9. Cómo obtener tu API key de TMDB
1. Crea una cuenta gratuita en TMDB.
2. Inicia sesión y entra a Settings > API.
3. Solicita una API key tipo Developer.
4. Copia la clave generada en la variable TMDB_API_KEY del archivo .env.



### Generar Django Secret Key

Colocar el siguiente comando en la terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


django-insecure-pegar codigo random
```

Copia la clave generada y reemplaza `tu_secret_key_de_django` en el archivo `.env`.




## 10. Problemas comunes (Troubleshooting)
- Error `OperationalError: no such column` o problemas similares al iniciar la app: ejecuta nuevamente `python manage.py migrate`.
- Error `TMDB_API_KEY not set` o resultados vacíos al buscar contenido: verifica que el archivo .env exista y que la variable TMDB_API_KEY esté bien configurada.
- Puerto 8000 ocupado: inicia el servidor en otro puerto con `python manage.py runserver 8001`.
- Error de importación de Django o paquetes: activa el entorno virtual y vuelve a ejecutar `pip install -r requirements.txt`.
- Problemas al subir fotos de perfil: verifica que la carpeta media/ exista y que tengas permisos de escritura.

## 11. Licencia y autor
- Autor: Angely Cabreja (axxe26)
- Año: 2026
- Licencia: Copyright propio
