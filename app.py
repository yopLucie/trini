import json
import os
import urllib.request
import urllib.error
import traceback
from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "llave_super_secreta_velogarage")

# ============================================================
# ☁️ CONFIGURACIÓN DE LA NUBE (RENDER + GITHUB GISTS) ☁️
# ============================================================
GIST_ID      = os.environ.get("GIST_ID")       
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  
ARCHIVO_DATOS = "datos_tienda.json"

# ============================================================
# 📦 BASE DE DATOS INICIAL
# ============================================================
DATOS_POR_DEFECTO = {
    "info": {
        "nombre":      "VeloGarage",
        "slogan":      "Tu bici, tu pasión, nuestro oficio.",
        "descripcion": "Reparamos, equipamos y apasionamos. Taller profesional con más de 12 años de experiencia en bicicletas de ruta, MTB, gravel y e-bikes.",
        "direccion":   "Av. Reforma 123, Ciudad de México, CDMX",
        "telefono":    "+52 55 1234 5678",
        "whatsapp":    "5215512345678",
        "email":       "hola@velogarage.com.mx",
        "maps_embed":  "https://maps.google.com/maps?q=Mexico%20City&t=&z=13&ie=UTF8&iwloc=&output=embed",
        "instagram":   "https://instagram.com/velogarage",
        "facebook":    "https://facebook.com/velogarage",
        "banco":       "BBVA",
        "titular":     "VeloGarage México",
        "clabe":       "012345678901234567",
        "qr_pago":     "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=012345678901234567",
        "anios":       "12",
        "clientes":    "800",
        "horarios": [
            {"dia": "Lunes – Viernes", "hora": "9:00 AM – 7:00 PM"},
            {"dia": "Sábado",          "hora": "10:00 AM – 3:00 PM"},
            {"dia": "Domingo",         "hora": "Cerrado"},
        ],
    },
    "ubicaciones": [
        {
            "id": 1, 
            "nombre": "Sucursal Matriz", 
            "direccion": "Av. Reforma 123, Ciudad de México, CDMX", 
            "maps_embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3762.661706692882!2d-99.16869362391038!3d19.42702454086111!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x85d1ff35f5bd1563%3A0x6c366f0e2de02ff7!2sEl%20%C3%81ngel%20de%20la%20Independencia!5e0!3m2!1ses-419!2smx!4v1700000000000!5m2!1ses-419!2smx"
        }
    ],
    "stats": [
        {"numero": "+800", "label": "Bicis reparadas"},
        {"numero": "12+",  "label": "Años de experiencia"},
        {"numero": "100%", "label": "Garantía en trabajo"},
    ],
    "bicicletas": [
        {"id": 1, "modelo": "Trek Marlin 7",       "descripcion": "MTB con suspensión delantera, frenos de disco hidráulicos Shimano y 24 velocidades.", "precio": 12500.00, "imagen": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600&q=80",  "badge": "Nuevo",   "talla": "Aro 29 · Talla M/L"},
        {"id": 2, "modelo": "Cannondale Synapse",   "descripcion": "Bicicleta de ruta endurance con cuadro SmartForm y grupo Shimano 105.",              "precio": 28900.50, "imagen": "https://images.unsplash.com/photo-1571333250630-f0230c320b6d?w=600&q=80",  "badge": "Premium", "talla": "Aro 700c · Talla S–XL"},
        {"id": 3, "modelo": "Trek FX 3 Disc",       "descripcion": "Bicicleta urbana híbrida, ligera y polivalente. Perfecta para ciudad y ciclovías.",   "precio": 6800.00,  "imagen": "https://images.unsplash.com/photo-1544191696-15693072e0aa?w=600&q=80",  "badge": "Popular", "talla": "Aro 700c · Unisex"},
    ],
    "accesorios": [
        {"id": 1, "nombre": "Casco Giro Syntax",       "descripcion": "Ventilación AURA, sistema Roc Loc 5. Certificación CE.",         "precio": 850.00,  "imagen": "https://images.unsplash.com/photo-1557803175-4a23c69a5d6d?w=600&q=80",  "badge": "Oferta"},
        {"id": 2, "nombre": "Zapatillas Shimano RC5",   "descripcion": "Suela de carbono, sistema BOA L6.",                               "precio": 1450.00, "imagen": "https://images.unsplash.com/photo-1622467827417-bbe2237067a9?w=600&q=80", "badge": ""},
        {"id": 3, "nombre": "Set Luces Knog Blinder",   "descripcion": "Delantera 80 lúm + trasera 44 lúm. USB-C.",                      "precio": 520.00,  "imagen": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&q=80",  "badge": ""},
        {"id": 4, "nombre": "Candado U-Lock Kryptonite","descripcion": "Acero endurecido, alta seguridad.",                               "precio": 900.00,  "imagen": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",  "badge": "Stock"},
    ],
    "repuestos": [
        {"id": 1, "nombre": "Grupo Shimano Deore 12v", "descripcion": "Kit completo: palancas, desviador, cassette y cadena.",      "precio": 2800.00, "imagen": "https://images.unsplash.com/photo-1558979158-65a1eaa08691?w=600&q=80",  "badge": ""},
        {"id": 2, "nombre": "Frenos Shimano BR-M315",  "descripcion": "Hidráulicos, compatibles con discos 160 y 180mm.",          "precio": 680.00,  "imagen": "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=600&q=80",  "badge": "Stock"},
        {"id": 3, "nombre": "Neumáticos Maxxis Ardent","descripcion": "Todo terreno, 27.5\" y 29\".",                              "precio": 380.00,  "imagen": "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=600&q=80",  "badge": ""},
        {"id": 4, "nombre": "Kit de Reparación",       "descripcion": "Parches, desmontadores, llave multiusos.",                  "precio": 320.00,  "imagen": "https://images.unsplash.com/photo-1588611910672-87c2b6cb08c1?w=600&q=80",  "badge": ""},
    ],
    "servicios": [
        {"icono": "🔧", "nombre": "Revisión completa",     "descripcion": "Inspección de frenos, cambios, rodamientos.",        "precio": "Desde $250"},
        {"icono": "⚙️", "nombre": "Cambio de transmisión", "descripcion": "Reemplazo de cadena, cassette, platos.",             "precio": "Desde $350"},
        {"icono": "🛞", "nombre": "Pinchazos y ruedas",    "descripcion": "Reparación y centrado de ruedas.",                   "precio": "Desde $80"},
        {"icono": "🏔️", "nombre": "Suspensión y frenos",   "descripcion": "Purga de frenos y servicio de horquillas.",         "precio": "Desde $450"},
        {"icono": "🎨", "nombre": "Pintura y estética",    "descripcion": "Restauración de cuadros y limpieza.",                "precio": "Desde $300"},
        {"icono": "⚡", "nombre": "Bicicletas eléctricas", "descripcion": "Mantenimiento de e-bikes: batería, motor.",          "precio": "Desde $600"},
    ],
    "marcas":  ["TREK", "SHIMANO", "SPECIALIZED", "SRAM", "MAXXIS", "FOX", "CAMPAGNOLO"],
    "resenas": [
        {"inicial": "CM", "nombre": "Carlos Morales",  "fecha": "Hace 2 semanas", "texto": "Súper profesionales y honestos con el presupuesto.",   "estrellas": 5},
        {"inicial": "VR", "nombre": "Valentina Rojas", "fecha": "Hace 1 mes",     "texto": "Me asesoraron increíblemente. Muy recomendable.",      "estrellas": 5},
        {"inicial": "JP", "nombre": "José Pérez",      "fecha": "Hace 3 semanas", "texto": "El mejor taller de la ciudad sin dudas.",              "estrellas": 5},
    ],
}

# ============================================================
# 🛠️ FUNCIONES GITHUB GIST CON ESCUDO ANTI-ERRORES
# ============================================================
def fusionar_seguro(base, nuevo):
    import copy
    res = copy.deepcopy(base)
    if "info" in nuevo and isinstance(nuevo["info"], dict):
        res["info"].update(nuevo["info"])
    for k in ["bicicletas", "accesorios", "repuestos", "servicios", "marcas", "resenas", "stats", "ubicaciones"]:
        if k in nuevo:
            res[k] = nuevo[k]
    return res

def obtener_datos():
    datos_base = DATOS_POR_DEFECTO

    if GIST_ID and GITHUB_TOKEN:
        try:
            url = f"https://api.github.com/gists/{GIST_ID}"
            req = urllib.request.Request(url, headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept":        "application/vnd.github.v3+json",
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                gist = json.loads(r.read().decode())

            archivos = gist.get("files", {})
            nombre_arch = "datos_tienda.json"
            if nombre_arch not in archivos and archivos:
                nombre_arch = list(archivos.keys())[0]

            if nombre_arch in archivos:
                contenido = archivos[nombre_arch].get("content", "{}")
                datos_gist = json.loads(contenido)
                if datos_gist:
                    return fusionar_seguro(datos_base, datos_gist)
        except Exception as e:
            print(f"⚠️ Error leyendo Gist: {e}")

    try:
        if not os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "w") as f:
                json.dump(DATOS_POR_DEFECTO, f, indent=4)
            return DATOS_POR_DEFECTO
        with open(ARCHIVO_DATOS, "r") as f:
            datos_local = json.load(f)
            return fusionar_seguro(datos_base, datos_local)
    except Exception as e:
        print(f"⚠️ Error local: {e}")
        return DATOS_POR_DEFECTO

def guardar_datos(datos_nuevos):
    datos_actuales = obtener_datos()
    datos_a_guardar = fusionar_seguro(datos_actuales, datos_nuevos)

    if GIST_ID and GITHUB_TOKEN:
        try:
            url     = f"https://api.github.com/gists/{GIST_ID}"
            payload = {"files": {"datos_tienda.json": {"content": json.dumps(datos_a_guardar, indent=4)}}}
            req     = urllib.request.Request(url,
                data=json.dumps(payload).encode(),
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept":        "application/vnd.github.v3+json",
                    "Content-Type":  "application/json",
                },
                method="PATCH")
            with urllib.request.urlopen(req, timeout=10):
                print("✅ Guardado en GitHub Gist")
        except Exception as e:
            print(f"⚠️ Error guardando en Gist: {e}")

    try:
        with open(ARCHIVO_DATOS, "w") as f:
            json.dump(datos_a_guardar, f, indent=4)
    except Exception:
        pass


# ============================================================
# 🎨 PLANTILLAS HTML
# ============================================================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-blue-50 flex items-center justify-center h-screen">
    <div class="bg-white p-8 rounded-xl shadow-2xl w-full max-w-sm border border-blue-100">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center"><span class="text-blue-600">🚲 Velo</span>Garage Admin</h2>
        {% if error %}<p class="text-red-500 text-sm mb-4 text-center">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña de admin" required
                class="w-full p-3 rounded bg-gray-50 text-gray-800 border border-gray-300 focus:border-blue-500 outline-none mb-4">
            <button type="submit" class="w-full bg-blue-600 text-white font-bold p-3 rounded hover:bg-blue-700 transition">Entrar</button>
            <a href="/" class="block text-center text-gray-500 mt-4 text-sm hover:text-blue-600">Volver a la tienda</a>
        </form>
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Admin - VeloGarage</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body class="bg-slate-50 pb-20">
    <div id="app">
        <nav class="bg-blue-900 text-white p-4 sticky top-0 z-50 shadow-md flex justify-between items-center">
            <h1 class="font-bold text-lg"><span class="text-blue-400">Velo</span>Garage Admin</h1>
            <div class="flex gap-4 items-center">
                <a href="/" target="_blank" class="text-blue-200 text-sm hover:text-white">Ver sitio ↗</a>
                <button @click="guardarCambios" :disabled="guardando"
                    class="bg-blue-600 px-4 py-2 rounded text-sm font-bold hover:bg-blue-500 shadow disabled:opacity-60 transition">
                    {{ guardando ? 'Guardando...' : '💾 Guardar Cambios' }}
                </button>
                <a href="/logout" class="text-blue-200 text-sm hover:text-white">Salir</a>
            </div>
        </nav>

        <div v-if="cargando" class="text-center p-10 text-gray-500">Cargando catálogo desde la nube...</div>

        <div v-else class="max-w-4xl mx-auto mt-6 px-4">
            <div class="flex overflow-x-auto gap-2 mb-6 pb-2 border-b border-gray-300">
                <button v-for="tab in tabs" @click="currentTab = tab.id"
                    :class="['px-4 py-2 rounded-t font-semibold whitespace-nowrap transition-colors',
                             currentTab === tab.id ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-blue-50']">
                    {{ tab.nombre }}
                </button>
            </div>

            <div v-show="currentTab === 'info'" class="bg-white p-6 rounded-lg shadow-md space-y-4 border border-blue-100">
                <h2 class="text-xl font-bold border-b pb-2 text-gray-800">Información del Negocio</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre</label><input v-model="datos.info.nombre" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Slogan</label><input v-model="datos.info.slogan" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Teléfono Público</label><input v-model="datos.info.telefono" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">WhatsApp (solo números)</label><input v-model="datos.info.whatsapp" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none" placeholder="5215512345678"></div>
                    <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Dirección</label><input v-model="datos.info.direccion" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Email</label><input v-model="datos.info.email" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Años de experiencia</label><input v-model="datos.info.anios" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Instagram (URL)</label><input v-model="datos.info.instagram" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Facebook (URL)</label><input v-model="datos.info.facebook" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    
                    <div class="md:col-span-2 mt-4"><h3 class="text-sm font-bold text-blue-600 uppercase border-b pb-1">Datos Bancarios / Pagos</h3></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Banco</label><input v-model="datos.info.banco" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Titular de la cuenta</label><input v-model="datos.info.titular" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">CLABE Interbancaria</label><input v-model="datos.info.clabe" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">URL Código QR (Opcional)</label><input v-model="datos.info.qr_pago" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none" placeholder="https://..."></div>
                    
                    <div class="md:col-span-2 mt-4">
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Horarios (uno por línea: Día: Hora)</label>
                        <textarea v-model="horariosTexto" rows="3" class="w-full border-2 border-gray-200 p-2 rounded focus:border-blue-500 outline-none font-mono text-sm" placeholder="Lunes – Viernes: 9:00 AM – 7:00 PM&#10;Sábado: 10:00 AM – 3:00 PM&#10;Domingo: Cerrado"></textarea>
                    </div>
                </div>
            </div>

            <div v-show="['bicicletas', 'accesorios', 'repuestos'].includes(currentTab)" class="space-y-6">
                <div class="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                    <h2 class="text-xl font-bold capitalize text-gray-800">Catálogo de {{ currentTab }}</h2>
                    <button @click="agregarItem(currentTab)" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-bold text-sm shadow transition">+ Nuevo Artículo</button>
                </div>

                <div v-for="(item, index) in datos[currentTab]" :key="index" class="bg-white p-5 rounded-lg shadow-md border-l-4 border-blue-500 relative hover:shadow-lg transition-shadow">
                    <button @click="eliminarItem(currentTab, index)" class="absolute top-3 right-3 text-red-400 hover:text-red-600 bg-red-50 hover:bg-red-100 rounded-full w-8 h-8 flex items-center justify-center font-bold">&times;</button>
                    <div class="flex items-start gap-4 mb-4">
                        <img v-if="item.imagen" :src="item.imagen" class="w-20 h-20 object-cover rounded border border-gray-200" alt="">
                        <div v-else class="w-20 h-20 bg-gray-50 rounded border border-gray-200 flex items-center justify-center text-xs text-gray-400 text-center">Sin<br>imagen</div>
                        <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre / Modelo</label>
                                <input v-if="currentTab === 'bicicletas'" v-model="item.modelo" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none">
                                <input v-else v-model="item.nombre" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Precio ($ MXN)</label>
                                <input type="number" v-model="item.precio" class="w-full border-2 border-gray-200 p-2 rounded text-sm font-bold text-purple-600 focus:border-blue-500 outline-none">
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Descripción</label><textarea v-model="item.descripcion" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none h-16"></textarea></div>
                        <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">URL de la imagen</label><input v-model="item.imagen" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none" placeholder="https://..."></div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Etiqueta (Nuevo, Oferta…)</label><input v-model="item.badge" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none"></div>
                        <div v-if="currentTab === 'bicicletas'"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Talla / Aro</label><input v-model="item.talla" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none"></div>
                    </div>
                </div>
                <div v-if="!datos[currentTab] || datos[currentTab].length === 0" class="text-center p-8 text-gray-500 bg-white rounded-lg shadow border-2 border-dashed border-gray-300">
                    No hay artículos aquí. Toca "+ Nuevo Artículo" para empezar.
                </div>
            </div>

            <div v-show="currentTab === 'ubicaciones'" class="space-y-6">
                <div class="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                    <h2 class="text-xl font-bold capitalize text-gray-800">Ubicaciones / Sucursales</h2>
                    <button @click="agregarItem('ubicaciones')" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-bold text-sm shadow transition">+ Nueva Ubicación</button>
                </div>

                <div v-for="(item, index) in datos.ubicaciones" :key="index" class="bg-white p-5 rounded-lg shadow-md border-l-4 border-blue-500 relative hover:shadow-lg transition-shadow">
                    <button @click="eliminarItem('ubicaciones', index)" class="absolute top-3 right-3 text-red-400 hover:text-red-600 bg-red-50 hover:bg-red-100 rounded-full w-8 h-8 flex items-center justify-center font-bold">&times;</button>
                    <div class="grid grid-cols-1 gap-3">
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre (Ej: Matriz, Sucursal Sur)</label><input v-model="item.nombre" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none"></div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Dirección Completa</label><input v-model="item.direccion" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none"></div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">URL de Google Maps (Solo el enlace src="...")</label><input v-model="item.maps_embed" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-blue-500 outline-none" placeholder="https://www.google.com/maps/embed?pb=..."></div>
                    </div>
                </div>
                <div v-if="!datos.ubicaciones || datos.ubicaciones.length === 0" class="text-center p-8 text-gray-500 bg-white rounded-lg shadow border-2 border-dashed border-gray-300">
                    No hay ubicaciones. Toca "+ Nueva Ubicación" para empezar.
                </div>
            </div>

        </div>
        <div v-if="mensaje" class="fixed bottom-4 right-4 bg-blue-900 text-white border-l-4 border-blue-400 px-6 py-4 rounded shadow-2xl font-bold">{{ mensaje }}</div>
    </div>
    <script>
    const { createApp } = Vue;
    createApp({
        data() {
            return {
                cargando: true, guardando: false, mensaje: '', currentTab: 'info',
                tabs: [{ id: 'info', nombre: '⚙️ General' }, { id: 'bicicletas', nombre: '🚲 Bicis' }, { id: 'accesorios', nombre: '🪖 Accesorios' }, { id: 'repuestos', nombre: '🔩 Repuestos' }, { id: 'ubicaciones', nombre: '📍 Ubicaciones' }],
                datos: { info: {}, bicicletas: [], accesorios: [], repuestos: [], ubicaciones: [] }, horariosTexto: '',
            };
        },
        methods: {
            async cargarDatos() {
                try {
                    const res  = await fetch('/api/datos');
                    const data = await res.json();
                    this.datos = Object.assign({ info: {}, bicicletas: [], accesorios: [], repuestos: [], ubicaciones: [] }, data);
                    if (this.datos.info.horarios) this.horariosTexto = this.datos.info.horarios.map(h => h.dia + ': ' + h.hora).join('\\n');
                } catch(e) { alert('Error cargando datos.'); } finally { this.cargando = false; }
            },
            agregarItem(cat) {
                if (!this.datos[cat]) this.datos[cat] = [];
                const nuevo = { id: Date.now(), descripcion: '', precio: 0, imagen: '', badge: '' };
                if (cat === 'bicicletas') { nuevo.modelo = 'Nueva Bici'; nuevo.talla = ''; } 
                else if (cat === 'ubicaciones') { nuevo.nombre = 'Nueva Sucursal'; nuevo.direccion = ''; nuevo.maps_embed = ''; }
                else { nuevo.nombre = 'Nuevo Artículo'; }
                this.datos[cat].unshift(nuevo);
            },
            eliminarItem(cat, idx) { if (confirm('¿Eliminar este artículo?')) this.datos[cat].splice(idx, 1); },
            async guardarCambios() {
                this.guardando = true; this.mensaje = '';
                if (this.horariosTexto) {
                    this.datos.info.horarios = this.horariosTexto.split('\\n').filter(l => l.includes(':')).map(l => {
                        const [dia, ...rest] = l.split(':'); return { dia: dia.trim(), hora: rest.join(':').trim() };
                    });
                }
                try {
                    const res = await fetch('/api/datos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(this.datos) });
                    if (res.ok) { this.mensaje = '✅ Cambios guardados en internet'; setTimeout(() => this.mensaje = '', 4000); } 
                    else { this.mensaje = '❌ Error al guardar'; setTimeout(() => this.mensaje = '', 5000); }
                } catch(e) { this.mensaje = '❌ Sin conexión'; setTimeout(() => this.mensaje = '', 5000); } finally { this.guardando = false; }
            },
        }, mounted() { this.cargarDatos(); },
    }).mount('#app');
    </script>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ info.nombre }} — Taller & Tienda de Bicicletas</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@700;900&display=swap" rel="stylesheet">
<style>
:root {
  /* Nuevo Tema Claro: Azul, Blanco, Morado */
  --bg-main: #F8FAFC;       /* Fondo principal (Blanco/Gris muy claro) */
  --bg-sec: #EFF6FF;        /* Fondo secundario (Azul muy clarito) */
  --bg-card: #FFFFFF;       /* Fondo de las tarjetas (Blanco puro) */
  --primary: #2563EB;       /* Azul Principal vibrante */
  --accent: #9333EA;        /* Morado para acentos y precios */
  --text-dark: #0F172A;     /* Texto principal (Casi negro/Azul marino) */
  --text-muted: #64748B;    /* Texto secundario (Gris pizarra) */
  --border-color: #E2E8F0;  /* Líneas divisorias */
  --bike-color: #2563EB;    /* Color de inicio para el Customizer */
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg-main);color:var(--text-dark);font-family:'Barlow',sans-serif;overflow-x:hidden;cursor:none;}

/* Custom Cursor */
.cursor{width:12px;height:12px;background:var(--primary);border-radius:50%;position:fixed;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);transition:width .2s,height .2s,background .2s;}
.cursor.hov{width:38px;height:38px;background:rgba(37,99,235,.15);border:2px solid var(--primary);}
@media(pointer:coarse){.cursor{display:none;}body{cursor:auto;}}

/* Navigation */
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1.1rem 3rem;background:rgba(255,255,255,.97);border-bottom:1px solid var(--border-color);backdrop-filter:blur(10px); box-shadow: 0 4px 20px rgba(0,0,0,0.03);}
.logo{font-family:'Bebas Neue',cursive;font-size:1.8rem;letter-spacing:.1em;color:var(--text-dark);text-decoration:none; cursor:pointer;}
.logo span{color:var(--primary);}
.nav-links{display:flex;gap:2rem;list-style:none;}
.nav-links button{background:none; border:none; color:var(--text-muted); font-family:'Barlow'; font-size:.82rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;cursor:pointer;transition:color .2s;}
.nav-links button:hover, .nav-links button.active-link {color:var(--primary);}
.nav-cta{background:var(--primary)!important;color:#fff!important;padding:.45rem 1.2rem; text-decoration:none; font-size:.82rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase; display:flex; align-items:center; border-radius:4px;}
.hamburger{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:4px;}
.hamburger span{display:block;width:24px;height:2px;background:var(--text-dark);}
.mob-menu{display:none;position:fixed;top:62px;left:0;right:0;background:rgba(255,255,255,.98);padding:2rem 3rem;border-bottom:1px solid var(--border-color);z-index:99; box-shadow: 0 10px 20px rgba(0,0,0,0.05);}
.mob-menu.open{display:block;}
.mob-menu button, .mob-menu a{display:block; width:100%; text-align:left; background:none; border:none; color:var(--text-muted);text-decoration:none;font-size:.9rem;font-family:'Barlow'; font-weight:700;letter-spacing:.15em;text-transform:uppercase;padding:.7rem 0;border-bottom:1px solid var(--border-color);cursor:pointer; transition:color .2s;}
.mob-menu button:hover, .mob-menu a:hover{color:var(--primary);}

/* --- SPA (Single Page Application) Logic --- */
.page-section { display: none; min-height: 100vh; padding-top: 80px; animation: fadeIn 0.4s ease-out forwards; }
.page-section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

/* Global Section Styles */
.section-title{font-family:'Bebas Neue',cursive;font-size:clamp(2.2rem,4.5vw,3.8rem);letter-spacing:.05em;line-height:1;}
.section-sub{color:var(--primary);font-size:.72rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;margin-bottom:.6rem;}
.line-h{width:50px;height:3px;background:var(--primary);display:inline-block;vertical-align:middle;margin-right:.8rem; border-radius:2px;}
.btn-primary{background:var(--primary);color:#fff;padding:.85rem 2rem;font-family:'Barlow';font-weight:700;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;border:none;cursor:pointer;transition:background .2s,transform .2s;display:inline-block; border-radius:4px;}
.btn-primary:hover{background:#1D4ED8;transform:translateY(-2px); box-shadow: 0 10px 15px rgba(37,99,235,0.2);}
.btn-secondary{background:transparent;color:var(--text-dark);padding:.85rem 2rem;font-family:'Barlow';font-weight:700;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;border:2px solid var(--border-color);cursor:pointer;transition:all .2s;display:inline-block; border-radius:4px;}
.btn-secondary:hover{border-color:var(--primary); color:var(--primary); transform:translateY(-2px);}

/* Hero Section */
.hero{display:grid;grid-template-columns:1fr 1fr;position:relative;overflow:hidden; padding-top:0;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 70% 50%,rgba(37,99,235,.08) 0%,transparent 60%);pointer-events:none;}
.hero-left{display:flex;flex-direction:column;justify-content:center;padding:8rem 3rem 5rem;}
.hero-tag{display:inline-flex;align-items:center;gap:.5rem;background:rgba(37,99,235,.1);border:1px solid rgba(37,99,235,.3);color:var(--primary);font-size:.72rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;padding:.4rem 1rem;margin-bottom:1.5rem;width:fit-content; border-radius:20px;}
.hero-title{font-family:'Bebas Neue',cursive;font-size:clamp(3.5rem,7vw,7rem);line-height:.92;letter-spacing:.02em;margin-bottom:1.5rem; color:var(--text-dark);}
.hero-title .accent{color:var(--primary);display:block;}
.hero-title .outline{-webkit-text-stroke:2px var(--text-dark);color:transparent;display:block;}
.hero-desc{color:var(--text-muted);font-size:.95rem;line-height:1.7;max-width:400px;margin-bottom:2.5rem; font-weight: 500;}
.hero-btns{display:flex;gap:1rem;flex-wrap:wrap;}
.hero-stats{display:flex;gap:2.5rem;margin-top:3.5rem;flex-wrap:wrap;}
.stat-num{font-family:'Barlow Condensed';font-size:2.3rem;font-weight:900;color:var(--accent);}
.stat-label{font-size:.72rem;color:var(--text-muted);letter-spacing:.1em;text-transform:uppercase; font-weight:700;}
.hero-right{position:relative;overflow:hidden;}
.hero-img{width:100%;height:100%;min-height:600px;object-fit:cover;}
.hero-overlay{position:absolute;inset:0;background:linear-gradient(to right,var(--bg-main) 0%, rgba(248,250,252,0.85) 25%, transparent 60%, rgba(255,255,255,.2) 100%);}

/* Marquee */
.marquee-wrap{background:var(--primary);padding:.75rem 0;overflow:hidden;white-space:nowrap;}
.marquee-inner{display:inline-block;animation:marquee 25s linear infinite;}
.marquee-inner span{font-family:'Bebas Neue';font-size:1.1rem;letter-spacing:.2em;color:#fff;margin:0 2rem;}
.marquee-inner span.dot{color:rgba(255,255,255,.5);font-size:.9rem;margin:0;}

/* Customizer (Mostrador Realista) */
.customizer-wrap { padding: 4rem 3rem; }
.custom-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 3rem; align-items: start; margin-top: 2rem; }
.realistic-viewer { background: var(--bg-sec); border-radius: 16px; overflow: hidden; position: relative; aspect-ratio: 4/3; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border-color); box-shadow: 0 20px 40px rgba(0,0,0,0.04); }
.realistic-img { width: 100%; height: 100%; object-fit: cover; object-position: center; transition: opacity 0.3s ease, transform 0.5s ease; }
.realistic-img.loading { opacity: 0.3; transform: scale(1.02); filter: blur(4px); }
.viewer-tag { position: absolute; top: 1.5rem; left: 1.5rem; background: rgba(255,255,255,0.9); padding: 0.4rem 1rem; border-radius: 30px; font-weight: 800; font-size: 0.75rem; color: var(--text-dark); box-shadow: 0 4px 10px rgba(0,0,0,0.05); letter-spacing: 0.1em; text-transform: uppercase; z-index: 10; backdrop-filter: blur(5px); }

.tools-panel { background: var(--bg-card); padding: 2rem; border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);}
.tool-title { font-family: 'Barlow Condensed'; font-size: 1.2rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem; border-bottom: 2px solid var(--bg-main); padding-bottom: .5rem; color:var(--text-dark);}
.model-selector { display: flex; flex-direction: column; gap: .5rem; margin-bottom: 2.5rem; }
.model-btn { background: transparent; border: 2px solid var(--border-color); color: var(--text-muted); padding: .8rem 1rem; font-family: 'Barlow'; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; cursor: pointer; transition: all .2s; text-align: left; display:flex; justify-content:space-between; align-items:center; border-radius:8px;}
.model-btn:hover, .model-btn.active { background: var(--bg-sec); border-color: var(--primary); color: var(--primary); }
.model-btn.active::after { content: '✓'; color: var(--primary); font-weight: 900;}

.color-palette { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.color-swatch { width: 100%; aspect-ratio: 1; border-radius: 50%; border: 3px solid #cbd5e1; cursor: pointer; transition: transform .2s, border-color .2s; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);}
.color-swatch:hover { transform: scale(1.1); border-color: #94a3b8;}
.color-swatch.active { border-color: var(--accent); transform: scale(1.15); box-shadow: 0 0 15px rgba(147,51,234,0.3);}

/* Services */
.services{padding:4rem 3rem;}
.services-header{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:3rem;flex-wrap:wrap;gap:1rem;}
.services-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1px;background:var(--border-color);border:1px solid var(--border-color); border-radius: 8px; overflow:hidden;}
.service-card{background:var(--bg-card);padding:2.5rem 2rem;transition:background .3s;}
.service-card:hover{background:var(--bg-sec);}
.service-icon{font-size:2rem;margin-bottom:1rem;display:block;}
.service-name{font-family:'Barlow Condensed';font-size:1.2rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.7rem; color:var(--text-dark);}
.service-desc{color:var(--text-muted);font-size:.88rem;line-height:1.6; font-weight:500;}
.service-price{margin-top:1.2rem;font-family:'Barlow Condensed';font-size:1.1rem;font-weight:700;color:var(--accent);}

/* Catalog */
.catalog{padding:4rem 3rem; background: var(--bg-sec);}
.catalog-header{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:2rem;flex-wrap:wrap;gap:1rem;}
.filters{display:flex;gap:.5rem;margin-bottom:2.5rem;flex-wrap:wrap;}
.filter-btn{background:var(--bg-card);border:1px solid var(--border-color);color:var(--text-muted);padding:.5rem 1.1rem;font-family:'Barlow';font-size:.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:all .2s; border-radius:20px;}
.filter-btn.active,.filter-btn:hover{background:var(--primary);border-color:var(--primary);color:#fff; box-shadow: 0 4px 10px rgba(37,99,235,0.2);}
.catalog-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:2rem;}
.product-card{background:var(--bg-card);overflow:hidden;position:relative;cursor:pointer;transition:all .3s;border:1px solid var(--border-color); border-radius:8px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);}
.product-card:hover{transform:translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); border-color: #cbd5e1;}
.prod-img{position:relative;aspect-ratio:4/3;overflow:hidden;background:#E2E8F0;}
.prod-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
.product-card:hover .prod-img img{transform:scale(1.05);}
.prod-badge{position:absolute;top:1rem;left:1rem;background:var(--primary);color:#fff;font-size:.62rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:.3rem .8rem; border-radius:4px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
.prod-info{padding:1.6rem;}
.prod-cat{font-size:.68rem;color:var(--primary);font-weight:800;letter-spacing:.2em;text-transform:uppercase;margin-bottom:.4rem;}
.prod-name{font-family:'Barlow Condensed';font-size:1.2rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem; color:var(--text-dark);}
.prod-desc{color:var(--text-muted);font-size:.85rem;line-height:1.5;margin-bottom:1.5rem; font-weight:500;}
.prod-footer{display:flex;align-items:center;justify-content:space-between;border-top:1px solid var(--border-color);padding-top:1rem;}
.prod-price{font-family:'Barlow Condensed';font-size:1.4rem;font-weight:900;color:var(--accent);}
.prod-price small{font-size:.75rem;color:var(--text-muted);font-weight:600;}
.btn-add{background:var(--bg-sec);color:var(--primary);border:none;padding:.5rem 1rem;font-family:'Barlow';font-weight:700;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:all .2s; border-radius:4px;}
.product-card:hover .btn-add{background:var(--primary); color:#fff;}
.product-card.hidden{display:none;}

/* Workshop & Testimonials */
.workshop{display:grid;grid-template-columns:1fr 1fr;}
.workshop-left{background:var(--primary);padding:5rem 3.5rem;display:flex;flex-direction:column;justify-content:center;}
.workshop-left .section-sub{color:rgba(255,255,255,0.7);}
.workshop-left .section-title{color:#fff;}
.workshop-left p{color:rgba(255,255,255,0.9);font-size:1rem;line-height:1.7;margin-top:1rem; font-weight:500;}
.workshop-btn{margin-top:2.5rem;background:#fff;color:var(--primary);padding:.85rem 2.2rem;font-family:'Barlow';font-weight:800;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;width:fit-content;display:inline-block;transition:all .2s; border:none; cursor:pointer; border-radius:4px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);}
.workshop-btn:hover{transform:translateY(-3px); box-shadow: 0 15px 25px rgba(0,0,0,0.15);}
.workshop-right{position:relative;min-height:450px;overflow:hidden;}
.workshop-right img{width:100%;height:100%;object-fit:cover;}

.testimonials{padding:4rem 3rem;}
.testimonials-header{text-align:center;margin-bottom:3rem;}
.reviews-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:2rem;}
.review-card{background:var(--bg-card);border:1px solid var(--border-color);padding:2.5rem;position:relative; border-radius:8px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);}
.review-stars{color:var(--accent);font-size:1rem;margin-bottom:1rem;}
.review-text{color:var(--text-muted);font-size:.9rem;line-height:1.7;margin-bottom:1.5rem; font-weight:500;}
.review-author{display:flex;align-items:center;gap:.8rem;border-top:1px solid var(--border-color);padding-top:1.2rem;}
.avatar{width:40px;height:40px;background:var(--primary);border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue';font-size:1.1rem;color:#fff;}
.author-name{font-weight:700;font-size:.85rem; color:var(--text-dark);}
.author-date{font-size:.75rem;color:var(--text-muted); font-weight:500;}
.quote-mark{position:absolute;top:1rem;right:1.5rem;font-family:'Bebas Neue';font-size:4rem;color:rgba(37,99,235,.05);line-height:1;}

/* Contact */
.contact{padding:4rem 3rem;display:grid;grid-template-columns:1fr 1fr;gap:5rem;align-items:start; background:var(--bg-sec);}
.contact-info p{color:var(--text-muted);line-height:1.8;margin:1.2rem 0 2rem; font-weight:500;}
.info-item{display:flex;gap:1rem;margin-bottom:1.4rem;align-items:flex-start;}
.info-icon{font-size:1.2rem;margin-top:.1rem;}
.info-label{font-size:.68rem;color:var(--primary);font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.2rem;}
.info-value{font-size:.95rem;color:var(--text-dark); font-weight:600;}
.contact-form{display:flex;flex-direction:column;gap:1.2rem; background:var(--bg-card); padding:2.5rem; border-radius:8px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); border: 1px solid var(--border-color);}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;}
.form-field{display:flex;flex-direction:column;gap:.4rem;}
.form-label{font-size:.7rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--text-muted);}
.form-input,.form-textarea,.form-select{background:var(--bg-main);border:2px solid var(--border-color);color:var(--text-dark);padding:.85rem 1rem;font-family:'Barlow';font-size:.9rem;transition:all .2s;width:100%;outline:none; border-radius:4px; font-weight:500;}
.form-input:focus,.form-textarea:focus,.form-select:focus{border-color:var(--primary); background:var(--bg-card); box-shadow: 0 0 0 3px rgba(37,99,235,0.1);}
.form-textarea{resize:vertical;min-height:120px;}
.form-submit{background:var(--primary);color:#fff;border:none;padding:1.1rem;font-family:'Barlow';font-weight:800;font-size:.9rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:all .2s; border-radius:4px; margin-top:.5rem;}
.form-submit:hover{background:#1D4ED8; box-shadow: 0 8px 20px rgba(37,99,235,0.2);}
.whatsapp-btn{display:flex;align-items:center;justify-content:center;gap:.6rem;background:#25D366;color:#fff;padding:.9rem;font-family:'Barlow';font-weight:800;font-size:.9rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;transition:background .2s; border-radius:4px;}
.whatsapp-btn:hover{background:#1ebe5d;}

footer{background:var(--text-dark);padding:4rem 3rem 2rem;}
.footer-top{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:3rem;margin-bottom:3rem;}
.footer-brand .logo{color:#fff;}
.footer-brand p{color:#94a3b8;font-size:.85rem;line-height:1.7;margin-top:1rem; font-weight:500;}
.footer-col h4{font-family:'Barlow Condensed';font-size:.9rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:#fff;margin-bottom:1.2rem;}
.footer-col ul{list-style:none;display:flex;flex-direction:column;gap:.7rem;}
.footer-col ul button, .footer-col ul a{background:none; border:none; text-align:left; color:#94a3b8;text-decoration:none;font-size:.85rem;transition:color .2s; cursor:pointer; font-weight:500;}
.footer-col ul button:hover, .footer-col ul a:hover{color:#60a5fa;}
.footer-bottom{border-top:1px solid #334155;padding-top:2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;}
.footer-bottom p{color:#64748b;font-size:.8rem; font-weight:500;}

.modal-overlay{display:none;position:fixed;inset:0;z-index:200;background:rgba(15,23,42,.8);backdrop-filter:blur(5px);align-items:center;justify-content:center;}
.modal-overlay.open{display:flex;}
.modal{background:var(--bg-card);border:1px solid var(--border-color);max-width:550px;width:90%;padding:2.5rem;position:relative;max-height:90vh;overflow-y:auto; border-radius:12px; box-shadow: 0 25px 50px rgba(0,0,0,0.15);}
.modal-close{position:absolute;top:1rem;right:1rem;background:var(--bg-main);border:1px solid var(--border-color);color:var(--text-muted);font-size:1.2rem;cursor:pointer; width:35px; height:35px; border-radius:50%; display:flex; align-items:center; justify-content:center; transition:all .2s;}
.modal-close:hover{color:var(--primary); border-color:var(--primary);}
.modal-img{width:100%;aspect-ratio:16/9;object-fit:cover;margin-bottom:1.5rem; border-radius:8px;}
.modal-title{font-family:'Barlow Condensed';font-size:1.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.3rem; color:var(--text-dark);}
.modal-cat{color:var(--primary);font-size:.75rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;margin-bottom:1rem;}
.modal-desc{color:var(--text-muted);font-size:.9rem;line-height:1.7;margin-bottom:1.5rem; font-weight:500;}
.modal-price{font-family:'Barlow Condensed';font-size:2.2rem;font-weight:900;color:var(--accent);}
.modal-actions{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-top:1rem; padding-top:1.5rem; border-top:1px solid var(--border-color);}
.toast{position:fixed;bottom:2rem;right:2rem;background:var(--text-dark);border-left:4px solid var(--primary);color:#fff;padding:1rem 1.5rem;font-size:.9rem; font-weight:600; z-index:300;transform:translateY(100px);opacity:0;transition:all .4s;max-width:300px; border-radius:4px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);}
.toast.show{transform:translateY(0);opacity:1;}

@media(max-width:1024px){.footer-top{grid-template-columns:1fr 1fr;}}
@media(max-width:768px){
  nav{padding:1rem 1.5rem;}.nav-links{display:none;}.hamburger{display:flex;}
  .hero{grid-template-columns:1fr;}.hero-right{min-height:320px;}.hero-left{padding:3rem 1.5rem;}
  .services,.catalog,.testimonials, .customizer-wrap{padding:3rem 1.5rem;}
  .custom-grid{grid-template-columns:1fr;}
  .workshop{grid-template-columns:1fr;}.workshop-left{padding:3.5rem 2rem;}.workshop-right{min-height:300px;}
  .contact{grid-template-columns:1fr;gap:2rem;padding:3rem 1.5rem;}.form-row{grid-template-columns:1fr;}
  .footer-top{grid-template-columns:1fr;}footer{padding:3rem 1.5rem 2rem;}
}
</style>
</head>
<body>
<div class="cursor" id="cursor"></div>

<!-- NAVIGATION -->
<nav>
  <button onclick="changeRoute('inicio')" class="logo">{{ info.nombre[:4] }}<span>{{ info.nombre[4:] }}</span></button>
  <ul class="nav-links">
    <li><button onclick="changeRoute('servicios')" data-target="servicios">Servicios</button></li>
    <li><button onclick="changeRoute('catalogo')" data-target="catalogo">Catálogo</button></li>
    <li><button onclick="changeRoute('modificaciones')" data-target="modificaciones">Modificaciones</button></li>
    <li><button onclick="changeRoute('taller')" data-target="taller">Taller</button></li>
    <li><button onclick="changeRoute('contacto')" data-target="contacto">Contacto</button></li>
    <li><a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="nav-cta">WhatsApp</a></li>
  </ul>
  <button class="hamburger" onclick="toggleMenu()"><span></span><span></span><span></span></button>
</nav>

<!-- MOBILE MENU -->
<div class="mob-menu" id="mobMenu">
  <button onclick="changeRoute('servicios')">Servicios</button>
  <button onclick="changeRoute('catalogo')">Catálogo</button>
  <button onclick="changeRoute('modificaciones')">Modificaciones</button>
  <button onclick="changeRoute('taller')">Taller</button>
  <button onclick="changeRoute('contacto')">Contacto</button>
  <a href="https://wa.me/{{ info.whatsapp }}" target="_blank">WhatsApp ↗</a>
  <a href="/admin" style="color:var(--primary);">⚙️ Admin</a>
</div>

<!-- MAIN CONTAINER -->
<main id="main-content">

  <!-- ================= INICIO ================= -->
  <section class="page-section active" id="inicio">
    <div class="hero">
      <div class="hero-left">
        <div class="hero-tag">🔧 Taller profesional & Tienda</div>
        <h1 class="hero-title"><span>Tu bici,</span><span class="accent">tu pasión,</span><span class="outline">nuestro oficio.</span></h1>
        <p class="hero-desc">{{ info.descripcion }}</p>
        <div class="hero-btns"><button onclick="changeRoute('catalogo')" class="btn-primary">Ver catálogo</button><button onclick="changeRoute('servicios')" class="btn-secondary">Nuestros servicios</button></div>
        <div class="hero-stats">{% for s in stats %}<div><div class="stat-num">{{ s.numero }}</div><div class="stat-label">{{ s.label }}</div></div>{% endfor %}</div>
      </div>
      <div class="hero-right">
        <img class="hero-img" src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&q=80" alt="Taller">
        <div class="hero-overlay"></div>
      </div>
    </div>
  </section>

  <!-- ================= MODIFICACIONES (REALISTA) ================= -->
  <section class="page-section" id="modificaciones">
    <div class="customizer-wrap">
      <div><div class="section-sub"><span class="line-h"></span>Vista Real</div><h2 class="section-title">Configurador de Estilos</h2></div>
      
      <div class="custom-grid">
        <!-- Visualizador Izquierda -->
        <div class="realistic-viewer">
            <div class="viewer-tag" id="viewerTag">Mountain Bike - Oscuro</div>
            <!-- Imagen base -->
            <img src="https://images.unsplash.com/photo-1576435728678-68ce0f6eb293?w=1200&q=80" alt="Bicicleta Real" id="realistic-img" class="realistic-img">
        </div>

        <!-- Panel de Herramientas Derecha -->
        <div class="tools-panel">
            <div class="tool-title">1. Selecciona el Modelo</div>
            <div class="model-selector">
                <button class="model-btn active" data-model="mtb" onclick="setBike('mtb', this)">Mountain Bike (MTB)</button>
                <button class="model-btn" data-model="ruta" onclick="setBike('ruta', this)">Bicicleta de Ruta</button>
                <button class="model-btn" data-model="urbana" onclick="setBike('urbana', this)">Urbana / Paseo</button>
            </div>

            <div class="tool-title">2. Color del Cuadro</div>
            <div class="color-palette">
                <!-- 8 colores base para un catálogo realista más amplio -->
                <div class="color-swatch active" data-color="oscuro" style="background:#1E293B;" onclick="setColor('oscuro', this)"></div>
                <div class="color-swatch" data-color="rojo" style="background:#E63946;" onclick="setColor('rojo', this)"></div>
                <div class="color-swatch" data-color="azul" style="background:#2563EB;" onclick="setColor('azul', this)"></div>
                <div class="color-swatch" data-color="claro" style="background:#F8FAFC;" onclick="setColor('claro', this)"></div>
                <div class="color-swatch" data-color="verde" style="background:#10B981;" onclick="setColor('verde', this)"></div>
                <div class="color-swatch" data-color="naranja" style="background:#F59E0B;" onclick="setColor('naranja', this)"></div>
                <div class="color-swatch" data-color="morado" style="background:#9333EA;" onclick="setColor('morado', this)"></div>
                <div class="color-swatch" data-color="plata" style="background:#94A3B8;" onclick="setColor('plata', this)"></div>
            </div>
            
            <div style="margin-top: 2.5rem;">
                <button onclick="changeRoute('contacto')" class="btn-primary" style="width:100%; text-align:center;">Cotizar este diseño</button>
            </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= TALLER ================= -->
  <section class="page-section" id="taller">
    <div class="workshop">
      <div class="workshop-left"><div class="section-sub">El taller</div><h2 class="section-title">Mecánicos<br>que aman<br>las bicis.</h2><p>Nuestro equipo tiene más de {{ info.anios }} años de experiencia reparando bicicletas.</p><p style="margin-top:.8rem">Garantía escrita y revisión de 30 días sin costo.</p><button onclick="changeRoute('contacto')" class="workshop-btn">Reservar turno 🔧</button></div>
      <div class="workshop-right"><img src="https://images.unsplash.com/photo-1619818586372-5e77cfb7aeeb?w=800&q=80" alt="Taller"></div>
    </div>
    
    <div class="testimonials">
      <div class="testimonials-header"><div class="section-sub"><span class="line-h"></span>Lo que dicen</div><h2 class="section-title">Clientes felices</h2></div>
      <div class="reviews-grid">{% for r in resenas %}<div class="review-card"><div class="quote-mark">"</div><div class="review-stars">{% for i in range(r.estrellas) %}★{% endfor %}</div><p class="review-text">{{ r.texto }}</p><div class="review-author"><div class="avatar">{{ r.inicial }}</div><div><div class="author-name">{{ r.nombre }}</div><div class="author-date">{{ r.fecha }}</div></div></div></div>{% endfor %}</div>
    </div>
  </section>

  <!-- ================= CONTACTO ================= -->
  <section class="page-section" id="contacto">
    <div class="contact">
      <div class="contact-info"><div class="section-sub"><span class="line-h"></span>Estamos aquí</div><h2 class="section-title">Contáctanos</h2><p>¿Quieres agendar una cita o saber más? Escríbenos o visítanos.</p>
        
        <div style="margin-bottom: 2rem;">
            {% for ubi in ubicaciones %}
            <div class="info-item" style="margin-bottom: 1.5rem; align-items: flex-start; padding-bottom: 1.5rem; border-bottom: 1px dashed var(--border-color);">
                <div class="info-icon" style="margin-right: 0.5rem; color: var(--primary);">📍</div>
                <div style="width: 100%;">
                    <div class="info-label">{{ ubi.nombre }}</div>
                    <div class="info-value" style="margin-bottom: 0.8rem;">{{ ubi.direccion }}</div>
                    {% if ubi.maps_embed %}
                    <div style="border:1px solid var(--border-color);overflow:hidden;height:180px;width:100%;border-radius:6px;">
                        <iframe width="100%" height="100%" frameborder="0" src="{{ ubi.maps_embed }}" style="filter:grayscale(30%) contrast(1.1);"></iframe>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="info-item"><div class="info-icon" style="color:var(--primary);">📞</div><div><div class="info-label">Teléfono</div><div class="info-value">{{ info.telefono }}</div></div></div>
        <div class="info-item"><div class="info-icon" style="color:var(--primary);">📧</div><div><div class="info-label">Email</div><div class="info-value">{{ info.email }}</div></div></div>
        <div class="info-item"><div class="info-icon" style="color:var(--primary);">🕐</div><div><div class="info-label">Horarios</div>{% for h in info.horarios %}<div class="info-value">{{ h.dia }}: {{ h.hora }}</div>{% endfor %}</div></div>
        
        <div style="margin-top:2rem; background:var(--bg-main); padding:1.5rem; border:1px solid var(--border-color); border-left:4px solid var(--accent); border-radius: 8px;">
          <div style="font-size:.68rem; color:var(--accent); font-weight:800; letter-spacing:.15em; text-transform:uppercase; margin-bottom:1rem;">Datos para Transferencia</div>
          <div style="display:flex; gap:1.5rem; align-items:center; flex-wrap:wrap;">
            {% if info.qr_pago %}
            <img src="{{ info.qr_pago }}" alt="QR de Pago" style="width:90px; height:90px; object-fit:contain; background:white; padding:5px; border-radius:6px; border: 1px solid #cbd5e1;">
            {% endif %}
            <div>
              <div style="font-size:.75rem; color:var(--text-muted); margin-bottom:.1rem;"><strong>Banco:</strong> <span style="color:var(--text-dark);">{{ info.banco }}</span></div>
              <div style="font-size:.75rem; color:var(--text-muted); margin-bottom:.4rem;"><strong>Titular:</strong> <span style="color:var(--text-dark);">{{ info.titular }}</span></div>
              <div style="font-size:.68rem; color:var(--primary); text-transform:uppercase; font-weight:700; letter-spacing:.1em; margin-bottom:.1rem;">CLABE Interbancaria</div>
              <div style="font-size:1.1rem; font-family:monospace; color:var(--text-dark); font-weight:800; letter-spacing:1px;">{{ info.clabe }}</div>
            </div>
          </div>
        </div>
      </div>
      <div><form class="contact-form" id="contactForm">
        <div class="form-row"><div class="form-field"><label class="form-label">Nombre</label><input type="text" class="form-input" id="fname" placeholder="Tu nombre" required></div><div class="form-field"><label class="form-label">Teléfono</label><input type="tel" class="form-input" id="fphone" placeholder="+52 55 ..."></div></div>
        <div class="form-field"><label class="form-label">Email</label><input type="email" class="form-input" id="femail" placeholder="tu@email.com" required></div>
        <div class="form-field"><label class="form-label">¿En qué podemos ayudarte?</label><select class="form-select" id="fservicio"><option value="">Selecciona una opción</option>{% for s in servicios %}<option>{{ s.nombre }}</option>{% endfor %}<option>Compra de bicicleta</option><option>Modificación / Pintura</option><option>Otro</option></select></div>
        <div class="form-field"><label class="form-label">Mensaje</label><textarea class="form-textarea" id="fmsg" placeholder="Cuéntanos más..."></textarea></div>
        <button type="submit" class="form-submit">Enviar mensaje →</button>
        <a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="whatsapp-btn">💬 Escribir por WhatsApp</a>
      </form></div>
    </div>
  </section>

</main>

<footer><div class="footer-top">
  <div class="footer-brand"><button onclick="changeRoute('inicio')" class="logo" style="background:none;border:none;">{{ info.nombre[:4] }}<span>{{ info.nombre[4:] }}</span></button><p>{{ info.descripcion }}</p></div>
  <div class="footer-col"><h4>Servicios</h4><ul>{% for s in servicios %}<li><button onclick="changeRoute('servicios')">{{ s.nombre }}</button></li>{% endfor %}</ul></div>
  <div class="footer-col"><h4>Tienda</h4><ul><li><button onclick="changeRoute('catalogo')">Bicicletas</button></li><li><button onclick="changeRoute('catalogo')">Accesorios</button></li><li><button onclick="changeRoute('catalogo')">Repuestos</button></li></ul></div>
  <div class="footer-col"><h4>Contacto</h4><ul>{% if info.instagram %}<li><a href="{{ info.instagram }}" target="_blank">Instagram</a></li>{% endif %}{% if info.facebook %}<li><a href="{{ info.facebook }}" target="_blank">Facebook</a></li>{% endif %}<li><a href="https://wa.me/{{ info.whatsapp }}" target="_blank">WhatsApp</a></li><li><a href="/admin">⚙️ Admin</a></li></ul></div>
</div><div class="footer-bottom"><p>© 2026 {{ info.nombre }}. Todos los derechos reservados.</p><p>Hecho con <span style="color:var(--primary);">♥</span> para los amantes de la bicicleta</p></div></footer>

<!-- Modals & Toasts -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)"><div class="modal" onclick="event.stopPropagation()"><button class="modal-close" onclick="closeModal()">✕</button><img src="" alt="" class="modal-img" id="modalImg"><div class="modal-cat" id="modalCat"></div><div class="modal-title" id="modalTitle"></div><div class="modal-desc" id="modalDesc"></div><div class="modal-actions"><div class="modal-price" id="modalPrice"></div><button class="btn-primary" onclick="changeRoute('contacto'); closeModal();">Consultar →</button></div></div></div>
<div class="toast" id="toast"></div>

<script>
// --- Custom Cursor ---
const cursor=document.getElementById('cursor');
document.addEventListener('mousemove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px';});
document.querySelectorAll('a, button, .product-card, .service-card, .filter-btn, .color-swatch, .model-btn, .modal-close').forEach(el=>{el.addEventListener('mouseenter',()=>cursor.classList.add('hov'));el.addEventListener('mouseleave',()=>cursor.classList.remove('hov'));});

// --- SPA Navigation System ---
function changeRoute(routeId) {
    // Esconder todas las secciones
    document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
    // Mostrar la sección destino
    document.getElementById(routeId).classList.add('active');
    
    // Actualizar color de botones del menú
    document.querySelectorAll('.nav-links button').forEach(btn => btn.classList.remove('active-link'));
    let activeBtn = document.querySelector(`.nav-links button[data-target="${routeId}"]`);
    if(activeBtn) activeBtn.classList.add('active-link');
    
    // Ir hasta arriba y cerrar menú móvil
    window.scrollTo(0, 0);
    document.getElementById('mobMenu').classList.remove('open');
}

// Check initial load hash (optional direct linking)
window.addEventListener('load', () => {
    let hash = window.location.hash.replace('#', '');
    if(hash && document.getElementById(hash)) { changeRoute(hash); }
});

function toggleMenu(){document.getElementById('mobMenu').classList.toggle('open');}

// --- Catalogo Filters ---
document.querySelectorAll('.filter-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');const f=btn.dataset.filter;document.querySelectorAll('.product-card').forEach(c=>{c.classList.toggle('hidden',f!=='all'&&c.dataset.cat!==f);});});});

// --- Modal System ---
function openModal(card){document.getElementById('modalImg').src=card.dataset.img;document.getElementById('modalCat').textContent=card.dataset.catLabel;document.getElementById('modalTitle').textContent=card.dataset.name;document.getElementById('modalDesc').textContent=card.dataset.desc;document.getElementById('modalPrice').textContent=card.dataset.price;document.getElementById('modalOverlay').classList.add('open');}
function closeModal(e){if(!e||e.target===document.getElementById('modalOverlay'))document.getElementById('modalOverlay').classList.remove('open');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});

// --- Contact Form ---
document.getElementById('contactForm').addEventListener('submit',async function(e){e.preventDefault();const btn=this.querySelector('.form-submit');btn.textContent='Enviando...';btn.disabled=true;try{const res=await fetch('/contacto',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:document.getElementById('fname').value,telefono:document.getElementById('fphone').value,email:document.getElementById('femail').value,servicio:document.getElementById('fservicio').value,mensaje:document.getElementById('fmsg').value})});const data=await res.json();showToast(data.ok?'✅ Mensaje enviado. Te contactamos pronto.':'⚠️ Error al enviar.');if(data.ok)this.reset();}catch{showToast('⚠️ Error. Escríbenos por WhatsApp.');}btn.textContent='Enviar mensaje →';btn.disabled=false;});
function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),4000);}

// --- Realistic Customizer Logic ---
const realisticImg = document.getElementById('realistic-img');
const viewerTag = document.getElementById('viewerTag');
let currentModel = 'mtb';
let currentColor = 'oscuro';

// Diccionario con fotografías 100% reales en alta calidad (Añadidos 4 colores extra)
const bikePhotos = {
    'mtb': {
        'oscuro': 'https://images.unsplash.com/photo-1576435728678-68ce0f6eb293?w=1200&q=80',
        'rojo': 'https://images.unsplash.com/photo-1558981359-219d6364c9c8?w=1200&q=80',
        'azul': 'https://images.unsplash.com/photo-1563212044-773df40fa2dd?w=1200&q=80',
        'claro': 'https://images.unsplash.com/photo-1544191696-102dbdaeeaa0?w=1200&q=80',
        'verde': 'https://images.unsplash.com/photo-1605553535914-41d3faec95eb?w=1200&q=80',
        'naranja': 'https://images.unsplash.com/photo-1533560904424-a0c61dc306fc?w=1200&q=80',
        'morado': 'https://images.unsplash.com/photo-1593018867503-4f27c73a21ba?w=1200&q=80',
        'plata': 'https://images.unsplash.com/photo-1610926950553-ebd024479e39?w=1200&q=80'
    },
    'ruta': {
        'oscuro': 'https://images.unsplash.com/photo-1571333250630-f0230c320b6d?w=1200&q=80',
        'rojo': 'https://images.unsplash.com/photo-1511994298241-608e28f14fde?w=1200&q=80',
        'azul': 'https://images.unsplash.com/photo-1559268950-2d7ceb2efa3a?w=1200&q=80',
        'claro': 'https://images.unsplash.com/photo-1484920274317-87885fcbc504?w=1200&q=80',
        'verde': 'https://images.unsplash.com/photo-1525826201389-9fc6267675ce?w=1200&q=80',
        'naranja': 'https://images.unsplash.com/photo-1505322022379-7c3353ee6291?w=1200&q=80',
        'morado': 'https://images.unsplash.com/photo-1618886487325-f665032b6352?w=1200&q=80',
        'plata': 'https://images.unsplash.com/photo-1534787238916-9ba6764efd4f?w=1200&q=80'
    },
    'urbana': {
        'oscuro': 'https://images.unsplash.com/photo-1471506480208-91b3a4cc78be?w=1200&q=80',
        'rojo': 'https://images.unsplash.com/photo-1507560461415-99731cfa9ace?w=1200&q=80',
        'azul': 'https://images.unsplash.com/photo-1520113412548-5240224df086?w=1200&q=80',
        'claro': 'https://images.unsplash.com/photo-1528629297340-d1d466945dc5?w=1200&q=80',
        'verde': 'https://images.unsplash.com/photo-1512106374988-c95f566d39ef?w=1200&q=80',
        'naranja': 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=80',
        'morado': 'https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=1200&q=80',
        'plata': 'https://images.unsplash.com/photo-1622340398608-be6329bb6d7a?w=1200&q=80'
    }
};

const modelNames = { 'mtb': 'Mountain Bike', 'ruta': 'Bici de Ruta', 'urbana': 'Urbana / Paseo' };
const colorNames = { 
    'oscuro': 'Estilo Oscuro', 'rojo': 'Estilo Rojo', 'azul': 'Estilo Azul', 'claro': 'Estilo Claro',
    'verde': 'Estilo Verde', 'naranja': 'Estilo Naranja', 'morado': 'Estilo Morado', 'plata': 'Estilo Plata'
};

function updateViewer() {
    // Añade efecto de desenfoque mientras carga la nueva foto real
    realisticImg.classList.add('loading');
    
    // Precarga de la nueva imagen
    const newImg = new Image();
    newImg.src = bikePhotos[currentModel][currentColor];
    newImg.onload = () => {
        realisticImg.src = newImg.src;
        realisticImg.classList.remove('loading');
        viewerTag.textContent = `${modelNames[currentModel]} - ${colorNames[currentColor]}`;
    };
}

function setBike(model, btnElement) {
    currentModel = model;
    document.querySelectorAll('.model-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');
    updateViewer();
}

function setColor(color, swatchElement) {
    currentColor = color;
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
    swatchElement.classList.add('active');
    updateViewer();
}
</script>
</body></html>
"""

# ============================================================
# 🚀 RUTAS (CON SISTEMA DE DIAGNÓSTICO EN PANTALLA)
# ============================================================
@app.route('/')
def inicio():
    try:
        datos = obtener_datos()
        return render_template_string(HTML_TEMPLATE, **datos)
    except Exception as e:
        error_info = traceback.format_exc()
        html_error = f"""
        <html><body style="background:#F8FAFC; color:#0F172A; padding:2rem; font-family:sans-serif;">
            <h1 style="color:#2563EB;">⚠️ Modo Diagnóstico</h1>
            <p>La página detectó un error al intentar dibujar el contenido. Mándale esto a tu programador:</p>
            <pre style="background:#FFFFFF; padding:1rem; color:#E63946; border-left: 4px solid #E63946; overflow-x: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">{error_info}</pre>
        </body></html>
        """
        return html_error, 500

@app.route('/contacto', methods=['POST'])
def contacto():
    d = request.get_json()
    print(f"\n📩 CONTACTO: {d.get('nombre')} | {d.get('email')}")
    return jsonify({"ok": True})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_admin = os.environ.get("ADMIN_PASSWORD", "admin123")
        if request.form.get('password') == password_admin:
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template_string(LOGIN_TEMPLATE, error="Contraseña incorrecta")
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('inicio'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return ADMIN_TEMPLATE

@app.route('/api/datos', methods=['GET'])
def api_get_datos():
    if not session.get('admin'):
        return jsonify({"error": "No autorizado"}), 403
    return jsonify(obtener_datos())

@app.route('/api/datos', methods=['POST'])
def api_post_datos():
    if not session.get('admin'):
        return jsonify({"error": "No autorizado"}), 403
    try:
        guardar_datos(request.get_json())
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=False, port=puerto)