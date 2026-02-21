import json
import os
import urllib.request
import urllib.error
import traceback
from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for

app = Flask(__name__)
# Genera una llave segura si no hay una en las variables de entorno
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

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
        "nombre":      "Taller de bicicletas Trinidad",
        "slogan":      "Tu bici, tu pasión, nuestro oficio.",
        "descripcion": "Reparamos, equipamos y apasionamos. Taller profesional con más de 12 años de experiencia en bicicletas de ruta, MTB, gravel y e-bikes.",
        "direccion":   "Av. Reforma 123, Ciudad de México, CDMX",
        "telefono":    "+52 55 1234 5678",
        "whatsapp":    "5215512345678",
        "email":       "hola@velogarage.com.mx",
        "maps_embed":  "https://maps.google.com/maps?q=Mexico%20City&t=&z=13&ie=UTF8&iwloc=&output=embed",
        "instagram":   "https://instagram.com/velogarage",
        "facebook":    "https://facebook.com/velogarage",
        "anios":       "12",
        "clientes":    "800",
        "horarios": [
            {"dia": "Lunes – Viernes", "hora": "9:00 AM – 7:00 PM"},
            {"dia": "Sábado",          "hora": "10:00 AM – 3:00 PM"},
            {"dia": "Domingo",         "hora": "Cerrado"},
        ],
    },
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
    for k in ["bicicletas", "accesorios", "repuestos", "servicios", "marcas", "resenas", "stats"]:
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
<body class="bg-gray-900 flex items-center justify-center h-screen">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-sm">
        <h2 class="text-2xl font-bold text-white mb-6 text-center text-orange-500">🚲 VeloGarage Admin</h2>
        {% if error %}<p class="text-red-500 text-sm mb-4 text-center">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña de admin" required
                class="w-full p-3 rounded bg-gray-700 text-white border border-gray-600 focus:border-orange-500 outline-none mb-4">
            <button type="submit" class="w-full bg-orange-500 text-white font-bold p-3 rounded hover:bg-orange-600">Entrar</button>
            <a href="/" class="block text-center text-gray-400 mt-4 text-sm hover:text-white">Volver a la tienda</a>
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
<body class="bg-gray-100 pb-20">
    <div id="app">
        <nav class="bg-gray-900 text-white p-4 sticky top-0 z-50 shadow flex justify-between items-center">
            <h1 class="font-bold text-lg"><span class="text-orange-500">Velo</span>Garage Admin</h1>
            <div class="flex gap-4 items-center">
                <a href="/" target="_blank" class="text-gray-400 text-sm hover:text-white">Ver sitio ↗</a>
                <button @click="guardarCambios" :disabled="guardando"
                    class="bg-orange-500 px-4 py-2 rounded text-sm font-bold hover:bg-orange-600 shadow disabled:opacity-60">
                    {{ guardando ? 'Guardando...' : '💾 Guardar Cambios' }}
                </button>
                <a href="/logout" class="text-gray-400 text-sm hover:text-white">Salir</a>
            </div>
        </nav>

        <div v-if="cargando" class="text-center p-10 text-gray-500">Cargando catálogo desde la nube...</div>

        <div v-else class="max-w-4xl mx-auto mt-6 px-4">
            <div class="flex overflow-x-auto gap-2 mb-6 pb-2 border-b border-gray-300">
                <button v-for="tab in tabs" @click="currentTab = tab.id"
                    :class="['px-4 py-2 rounded-t font-semibold whitespace-nowrap transition-colors',
                             currentTab === tab.id ? 'bg-orange-500 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-200']">
                    {{ tab.nombre }}
                </button>
            </div>

            <div v-show="currentTab === 'info'" class="bg-white p-6 rounded-lg shadow-md space-y-4">
                <h2 class="text-xl font-bold border-b pb-2 text-gray-800">Información del Negocio</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre</label><input v-model="datos.info.nombre" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Slogan</label><input v-model="datos.info.slogan" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Teléfono Público</label><input v-model="datos.info.telefono" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">WhatsApp (solo números)</label><input v-model="datos.info.whatsapp" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none" placeholder="5215512345678"></div>
                    <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Dirección</label><input v-model="datos.info.direccion" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Email</label><input v-model="datos.info.email" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Años de experiencia</label><input v-model="datos.info.anios" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Instagram (URL)</label><input v-model="datos.info.instagram" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Facebook (URL)</label><input v-model="datos.info.facebook" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none"></div>
                    <div class="md:col-span-2">
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Horarios (uno por línea: Día: Hora)</label>
                        <textarea v-model="horariosTexto" rows="3" class="w-full border-2 border-gray-200 p-2 rounded focus:border-orange-500 outline-none font-mono text-sm" placeholder="Lunes – Viernes: 9:00 AM – 7:00 PM&#10;Sábado: 10:00 AM – 3:00 PM&#10;Domingo: Cerrado"></textarea>
                    </div>
                </div>
            </div>

            <div v-show="['bicicletas', 'accesorios', 'repuestos'].includes(currentTab)" class="space-y-6">
                <div class="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
                    <h2 class="text-xl font-bold capitalize text-gray-800">Catálogo de {{ currentTab }}</h2>
                    <button @click="agregarItem(currentTab)" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded font-bold text-sm shadow transition">+ Nuevo Artículo</button>
                </div>

                <div v-for="(item, index) in datos[currentTab]" :key="index" class="bg-white p-5 rounded-lg shadow-md border-l-4 border-orange-500 relative hover:shadow-lg transition-shadow">
                    <button @click="eliminarItem(currentTab, index)" class="absolute top-3 right-3 text-red-400 hover:text-red-600 bg-red-50 hover:bg-red-100 rounded-full w-8 h-8 flex items-center justify-center font-bold">&times;</button>
                    <div class="flex items-start gap-4 mb-4">
                        <img v-if="item.imagen" :src="item.imagen" class="w-20 h-20 object-cover rounded border border-gray-200" alt="">
                        <div v-else class="w-20 h-20 bg-gray-100 rounded border border-gray-200 flex items-center justify-center text-xs text-gray-400 text-center">Sin<br>imagen</div>
                        <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre / Modelo</label>
                                <input v-if="currentTab === 'bicicletas'" v-model="item.modelo" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none">
                                <input v-else v-model="item.nombre" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Precio ($ MXN)</label>
                                <input type="number" v-model="item.precio" class="w-full border-2 border-gray-200 p-2 rounded text-sm font-bold text-green-600 focus:border-orange-500 outline-none">
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Descripción</label><textarea v-model="item.descripcion" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none h-16"></textarea></div>
                        <div class="md:col-span-2"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">URL de la imagen</label><input v-model="item.imagen" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none" placeholder="https://..."></div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Etiqueta (Nuevo, Oferta…)</label><input v-model="item.badge" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none"></div>
                        <div v-if="currentTab === 'bicicletas'"><label class="block text-xs font-bold text-gray-500 uppercase mb-1">Talla / Aro</label><input v-model="item.talla" class="w-full border-2 border-gray-200 p-2 rounded text-sm focus:border-orange-500 outline-none"></div>
                    </div>
                </div>
                <div v-if="!datos[currentTab] || datos[currentTab].length === 0" class="text-center p-8 text-gray-500 bg-white rounded-lg shadow border-2 border-dashed border-gray-300">
                    No hay artículos aquí. Toca "+ Nuevo Artículo" para empezar.
                </div>
            </div>
        </div>
        <div v-if="mensaje" class="fixed bottom-4 right-4 bg-gray-900 text-white border-l-4 border-orange-500 px-6 py-4 rounded shadow-2xl font-bold">{{ mensaje }}</div>
    </div>
    <script>
    const { createApp } = Vue;
    createApp({
        data() {
            return {
                cargando: true, guardando: false, mensaje: '', currentTab: 'bicicletas',
                tabs: [{ id: 'info', nombre: '⚙️ General' }, { id: 'bicicletas', nombre: '🚲 Bicis' }, { id: 'accesorios', nombre: '🪖 Accesorios' }, { id: 'repuestos', nombre: '🔩 Repuestos' }],
                datos: { info: {}, bicicletas: [], accesorios: [], repuestos: [] }, horariosTexto: '',
            };
        },
        methods: {
            async cargarDatos() {
                try {
                    const res  = await fetch('/api/datos');
                    const data = await res.json();
                    this.datos = Object.assign({ info: {}, bicicletas: [], accesorios: [], repuestos: [] }, data);
                    if (this.datos.info.horarios) this.horariosTexto = this.datos.info.horarios.map(h => h.dia + ': ' + h.hora).join('\\n');
                } catch(e) { alert('Error cargando datos.'); } finally { this.cargando = false; }
            },
            agregarItem(cat) {
                if (!this.datos[cat]) this.datos[cat] = [];
                const nuevo = { id: Date.now(), descripcion: '', precio: 0, imagen: '', badge: '' };
                if (cat === 'bicicletas') { nuevo.modelo = 'Nueva Bici'; nuevo.talla = ''; } else { nuevo.nombre = 'Nuevo Artículo'; }
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
:root{--black:#0a0a0a;--dark:#111111;--card:#1a1a1a;--orange:#FF5500;--yellow:#FFD000;--white:#f5f5f0;--gray:#888;--lg:#2a2a2a;}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{background:var(--black);color:var(--white);font-family:'Barlow',sans-serif;overflow-x:hidden;cursor:none;}
.cursor{width:12px;height:12px;background:var(--orange);border-radius:50%;position:fixed;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);transition:width .2s,height .2s,background .2s;}
.cursor.hov{width:38px;height:38px;background:rgba(255,85,0,.2);border:2px solid var(--orange);}
@media(pointer:coarse){.cursor{display:none;}body{cursor:auto;}}
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1.1rem 3rem;background:rgba(10,10,10,.97);border-bottom:1px solid #1e1e1e;backdrop-filter:blur(10px);}
.logo{font-family:'Bebas Neue',cursive;font-size:1.8rem;letter-spacing:.1em;color:var(--white);text-decoration:none;}
.logo span{color:var(--orange);}
.nav-links{display:flex;gap:2.5rem;list-style:none;}
.nav-links a{color:var(--gray);text-decoration:none;font-size:.82rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;transition:color .2s;}
.nav-links a:hover{color:var(--orange);}
.nav-cta{background:var(--orange)!important;color:var(--white)!important;padding:.45rem 1.2rem;}
.hamburger{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:4px;}
.hamburger span{display:block;width:24px;height:2px;background:var(--white);}
.mob-menu{display:none;position:fixed;top:62px;left:0;right:0;background:rgba(10,10,10,.98);padding:2rem 3rem;border-bottom:1px solid #222;z-index:99;}
.mob-menu.open{display:block;}
.mob-menu a{display:block;color:var(--gray);text-decoration:none;font-size:.9rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;padding:.7rem 0;border-bottom:1px solid #1a1a1a;transition:color .2s;}
.mob-menu a:hover{color:var(--orange);}
.hero{min-height:100vh;display:grid;grid-template-columns:1fr 1fr;padding-top:65px;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 70% 50%,rgba(255,85,0,.08) 0%,transparent 60%);pointer-events:none;}
.hero-left{display:flex;flex-direction:column;justify-content:center;padding:5rem 3rem;}
.hero-tag{display:inline-flex;align-items:center;gap:.5rem;background:rgba(255,85,0,.1);border:1px solid rgba(255,85,0,.3);color:var(--orange);font-size:.72rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;padding:.4rem 1rem;margin-bottom:1.5rem;width:fit-content;}
.hero-title{font-family:'Bebas Neue',cursive;font-size:clamp(3.5rem,7vw,7rem);line-height:.92;letter-spacing:.02em;margin-bottom:1.5rem;}
.hero-title .accent{color:var(--orange);display:block;}
.hero-title .outline{-webkit-text-stroke:2px var(--white);color:transparent;display:block;}
.hero-desc{color:var(--gray);font-size:.95rem;line-height:1.7;max-width:400px;margin-bottom:2.5rem;}
.hero-btns{display:flex;gap:1rem;flex-wrap:wrap;}
.btn-primary{background:var(--orange);color:var(--white);padding:.85rem 2rem;font-family:'Barlow';font-weight:700;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;border:none;cursor:pointer;transition:background .2s,transform .2s;display:inline-block;}
.btn-primary:hover{background:#ff7733;transform:translateY(-2px);}
.btn-secondary{background:transparent;color:var(--white);padding:.85rem 2rem;font-family:'Barlow';font-weight:700;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;border:1px solid #444;cursor:pointer;transition:border-color .2s,transform .2s;display:inline-block;}
.btn-secondary:hover{border-color:var(--white);transform:translateY(-2px);}
.hero-stats{display:flex;gap:2.5rem;margin-top:3.5rem;flex-wrap:wrap;}
.stat-num{font-family:'Barlow Condensed';font-size:2.3rem;font-weight:900;color:var(--yellow);}
.stat-label{font-size:.72rem;color:var(--gray);letter-spacing:.1em;text-transform:uppercase;}
.hero-right{position:relative;overflow:hidden;}
.hero-img{width:100%;height:100%;min-height:600px;object-fit:cover;filter:grayscale(30%) contrast(1.1);}
.hero-overlay{position:absolute;inset:0;background:linear-gradient(to right,var(--black) 0%,transparent 30%,transparent 70%,rgba(0,0,0,.4) 100%);}
.hero-badge{position:absolute;bottom:3rem;right:2rem;background:var(--orange);width:105px;height:105px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;animation:spin 8s linear infinite;}
.hero-badge span{font-family:'Bebas Neue';font-size:.95rem;letter-spacing:.1em;color:var(--white);line-height:1.1;text-align:center;}
.marquee-wrap{background:var(--orange);padding:.75rem 0;overflow:hidden;white-space:nowrap;}
.marquee-inner{display:inline-block;animation:marquee 22s linear infinite;}
.marquee-inner span{font-family:'Bebas Neue';font-size:1.1rem;letter-spacing:.2em;color:var(--black);margin:0 2rem;}
.marquee-inner span.dot{color:rgba(0,0,0,.4);font-size:.9rem;margin:0;}
.section-title{font-family:'Bebas Neue',cursive;font-size:clamp(2.2rem,4.5vw,3.8rem);letter-spacing:.05em;line-height:1;}
.section-sub{color:var(--orange);font-size:.72rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;margin-bottom:.6rem;}
.line-h{width:50px;height:2px;background:var(--orange);display:inline-block;vertical-align:middle;margin-right:.8rem;}
.services{padding:6rem 3rem;}
.services-header{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:3rem;flex-wrap:wrap;gap:1rem;}
.services-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.5px;background:#222;border:1.5px solid #222;}
.service-card{background:var(--dark);padding:2.5rem 2rem;transition:background .3s;}
.service-card:hover{background:var(--card);}
.service-icon{font-size:2rem;margin-bottom:1rem;display:block;}
.service-name{font-family:'Barlow Condensed';font-size:1.2rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.7rem;}
.service-desc{color:var(--gray);font-size:.88rem;line-height:1.6;}
.service-price{margin-top:1.2rem;font-family:'Barlow Condensed';font-size:1.1rem;font-weight:700;color:var(--yellow);}
.catalog{padding:6rem 3rem;background:var(--dark);position:relative;}
.catalog::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(to right,transparent,var(--orange),transparent);}
.catalog-header{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:2rem;flex-wrap:wrap;gap:1rem;}
.filters{display:flex;gap:.5rem;margin-bottom:2.5rem;flex-wrap:wrap;}
.filter-btn{background:transparent;border:1px solid #333;color:var(--gray);padding:.5rem 1.1rem;font-family:'Barlow';font-size:.78rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:all .2s;}
.filter-btn.active,.filter-btn:hover{background:var(--orange);border-color:var(--orange);color:var(--white);}
.catalog-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1.5rem;}
.product-card{background:var(--card);overflow:hidden;position:relative;cursor:pointer;transition:transform .3s;border:1px solid #222;}
.product-card:hover{transform:translateY(-4px);}
.prod-img{position:relative;aspect-ratio:4/3;overflow:hidden;background:#1e1e1e;}
.prod-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
.product-card:hover .prod-img img{transform:scale(1.04);}
.prod-badge{position:absolute;top:.8rem;left:.8rem;background:var(--orange);color:var(--white);font-size:.62rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:.25rem .6rem;}
.prod-info{padding:1.4rem;}
.prod-cat{font-size:.68rem;color:var(--orange);font-weight:700;letter-spacing:.2em;text-transform:uppercase;margin-bottom:.3rem;}
.prod-name{font-family:'Barlow Condensed';font-size:1.15rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.4rem;}
.prod-desc{color:var(--gray);font-size:.8rem;line-height:1.5;margin-bottom:1.1rem;}
.prod-footer{display:flex;align-items:center;justify-content:space-between;border-top:1px solid #2a2a2a;padding-top:.9rem;}
.prod-price{font-family:'Barlow Condensed';font-size:1.35rem;font-weight:900;color:var(--yellow);}
.prod-price small{font-size:.75rem;color:var(--gray);font-weight:400;}
.btn-add{background:var(--orange);color:var(--white);border:none;padding:.45rem .9rem;font-family:'Barlow';font-weight:700;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:background .2s;}
.btn-add:hover{background:#ff7733;}
.product-card.hidden{display:none;}
.workshop{display:grid;grid-template-columns:1fr 1fr;}
.workshop-left{background:var(--orange);padding:5rem 3.5rem;display:flex;flex-direction:column;justify-content:center;}
.workshop-left .section-sub{color:rgba(0,0,0,.5);}
.workshop-left .section-title{color:var(--black);}
.workshop-left p{color:rgba(0,0,0,.7);font-size:.95rem;line-height:1.7;margin-top:1rem;}
.workshop-btn{margin-top:2rem;background:var(--black);color:var(--white);padding:.85rem 2.2rem;font-family:'Barlow';font-weight:700;font-size:.83rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;width:fit-content;display:inline-block;transition:opacity .2s;}
.workshop-btn:hover{opacity:.8;}
.workshop-right{position:relative;min-height:450px;overflow:hidden;}
.workshop-right img{width:100%;height:100%;object-fit:cover;filter:grayscale(40%);}
.workshop-right::after{content:'';position:absolute;inset:0;background:linear-gradient(to right,var(--orange) 0%,transparent 25%);}
.brands{padding:3.5rem 3rem;border-top:1px solid #1a1a1a;border-bottom:1px solid #1a1a1a;}
.brands-label{font-size:.68rem;color:#444;letter-spacing:.2em;text-transform:uppercase;text-align:center;margin-bottom:1.8rem;}
.brands-row{display:flex;align-items:center;justify-content:center;gap:3rem;flex-wrap:wrap;}
.brand-name{font-family:'Bebas Neue';font-size:1.5rem;letter-spacing:.15em;color:#333;transition:color .3s;}
.brand-name:hover{color:var(--white);}
.testimonials{padding:6rem 3rem;background:var(--dark);}
.testimonials-header{text-align:center;margin-bottom:3rem;}
.reviews-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:1.5rem;}
.review-card{background:var(--card);border:1px solid #222;padding:2rem;position:relative;}
.review-stars{color:var(--yellow);font-size:.85rem;margin-bottom:.8rem;}
.review-text{color:#ccc;font-size:.88rem;line-height:1.7;margin-bottom:1.3rem;}
.review-author{display:flex;align-items:center;gap:.8rem;border-top:1px solid #2a2a2a;padding-top:.9rem;}
.avatar{width:36px;height:36px;background:var(--orange);border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue';font-size:.95rem;color:var(--white);}
.author-name{font-weight:700;font-size:.83rem;}
.author-date{font-size:.72rem;color:var(--gray);}
.quote-mark{position:absolute;top:1rem;right:1.2rem;font-family:'Bebas Neue';font-size:3.5rem;color:rgba(255,85,0,.1);line-height:1;}
.contact{padding:6rem 3rem;display:grid;grid-template-columns:1fr 1fr;gap:5rem;align-items:start;}
.contact-info p{color:var(--gray);line-height:1.8;margin:1.2rem 0 2rem;}
.info-item{display:flex;gap:1rem;margin-bottom:1.4rem;align-items:flex-start;}
.info-icon{font-size:1.1rem;margin-top:.1rem;}
.info-label{font-size:.68rem;color:var(--orange);font-weight:700;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.2rem;}
.info-value{font-size:.92rem;color:var(--white);}
.contact-form{display:flex;flex-direction:column;gap:1rem;}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem;}
.form-field{display:flex;flex-direction:column;gap:.35rem;}
.form-label{font-size:.68rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--gray);}
.form-input,.form-textarea,.form-select{background:var(--card);border:1px solid #2a2a2a;color:var(--white);padding:.75rem .9rem;font-family:'Barlow';font-size:.88rem;transition:border-color .2s;width:100%;outline:none;}
.form-input:focus,.form-textarea:focus,.form-select:focus{border-color:var(--orange);}
.form-textarea{resize:vertical;min-height:110px;}
.form-select option{background:var(--dark);}
.form-submit{background:var(--orange);color:var(--white);border:none;padding:1rem;font-family:'Barlow';font-weight:700;font-size:.88rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:background .2s;}
.form-submit:hover{background:#ff7733;}
.whatsapp-btn{display:flex;align-items:center;justify-content:center;gap:.6rem;background:#25D366;color:var(--white);padding:.85rem;font-family:'Barlow';font-weight:700;font-size:.88rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;transition:background .2s;margin-top:.5rem;}
.whatsapp-btn:hover{background:#1ebe5d;}
footer{background:var(--black);border-top:1px solid #1a1a1a;padding:3.5rem 3rem 2rem;}
.footer-top{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:3rem;margin-bottom:2.5rem;}
.footer-brand p{color:var(--gray);font-size:.83rem;line-height:1.7;margin-top:.8rem;}
.footer-col h4{font-family:'Barlow Condensed';font-size:.85rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--white);margin-bottom:1rem;}
.footer-col ul{list-style:none;display:flex;flex-direction:column;gap:.55rem;}
.footer-col ul a{color:var(--gray);text-decoration:none;font-size:.83rem;transition:color .2s;}
.footer-col ul a:hover{color:var(--orange);}
.footer-bottom{border-top:1px solid #1a1a1a;padding-top:1.5rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;}
.footer-bottom p{color:#444;font-size:.78rem;}
.orange{color:var(--orange);}
.modal-overlay{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.88);backdrop-filter:blur(5px);align-items:center;justify-content:center;}
.modal-overlay.open{display:flex;}
.modal{background:var(--card);border:1px solid #333;max-width:500px;width:90%;padding:2.5rem;position:relative;max-height:90vh;overflow-y:auto;}
.modal-close{position:absolute;top:1rem;right:1rem;background:none;border:none;color:var(--gray);font-size:1.3rem;cursor:pointer;}
.modal-close:hover{color:var(--orange);}
.modal-img{width:100%;aspect-ratio:16/9;object-fit:cover;margin-bottom:1.3rem;}
.modal-title{font-family:'Barlow Condensed';font-size:1.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.2rem;}
.modal-cat{color:var(--orange);font-size:.72rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;margin-bottom:.9rem;}
.modal-desc{color:var(--gray);font-size:.88rem;line-height:1.7;margin-bottom:1.3rem;}
.modal-price{font-family:'Barlow Condensed';font-size:2rem;font-weight:900;color:var(--yellow);}
.modal-actions{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-top:1rem;}
.toast{position:fixed;bottom:2rem;right:2rem;background:var(--card);border-left:4px solid var(--orange);color:var(--white);padding:.9rem 1.3rem;font-size:.85rem;z-index:300;transform:translateY(100px);opacity:0;transition:all .4s;max-width:300px;}
.toast.show{transform:translateY(0);opacity:1;}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@media(max-width:1024px){.footer-top{grid-template-columns:1fr 1fr;}}
@media(max-width:768px){
  nav{padding:1rem 1.5rem;}.nav-links{display:none;}.hamburger{display:flex;}
  .hero{grid-template-columns:1fr;}.hero-right{min-height:320px;}.hero-left{padding:3rem 1.5rem;}
  .services,.catalog,.testimonials{padding:4rem 1.5rem;}
  .workshop{grid-template-columns:1fr;}.workshop-left{padding:3.5rem 2rem;}.workshop-right{min-height:300px;}
  .contact{grid-template-columns:1fr;gap:2rem;padding:4rem 1.5rem;}.form-row{grid-template-columns:1fr;}
  .footer-top{grid-template-columns:1fr;}footer{padding:3rem 1.5rem 2rem;}.brands{padding:2.5rem 1.5rem;}
}
</style>
</head>
<body>
<div class="cursor" id="cursor"></div>
<nav>
  <a href="#inicio" class="logo">{{ info.nombre[:4] }}<span>{{ info.nombre[4:] }}</span></a>
  <ul class="nav-links">
    <li><a href="#servicios">Servicios</a></li>
    <li><a href="#catalogo">Catálogo</a></li>
    <li><a href="#taller">Taller</a></li>
    <li><a href="#contacto">Contacto</a></li>
    <li><a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="nav-cta">WhatsApp</a></li>
  </ul>
  <button class="hamburger" onclick="toggleMenu()"><span></span><span></span><span></span></button>
</nav>
<div class="mob-menu" id="mobMenu">
  <a href="#servicios" onclick="toggleMenu()">Servicios</a>
  <a href="#catalogo" onclick="toggleMenu()">Catálogo</a>
  <a href="#taller" onclick="toggleMenu()">Taller</a>
  <a href="#contacto" onclick="toggleMenu()">Contacto</a>
  <a href="https://wa.me/{{ info.whatsapp }}" target="_blank">WhatsApp ↗</a>
  <a href="/admin">⚙️ Admin</a>
</div>

<section class="hero" id="inicio">
  <div class="hero-left">
    <div class="hero-tag">🔧 Taller profesional & Tienda</div>
    <h1 class="hero-title"><span>Tu bici,</span><span class="accent">tu pasión,</span><span class="outline">nuestro oficio.</span></h1>
    <p class="hero-desc">{{ info.descripcion }}</p>
    <div class="hero-btns"><a href="#catalogo" class="btn-primary">Ver catálogo</a><a href="#servicios" class="btn-secondary">Nuestros servicios</a></div>
    <div class="hero-stats">{% for s in stats %}<div><div class="stat-num">{{ s.numero }}</div><div class="stat-label">{{ s.label }}</div></div>{% endfor %}</div>
  </div>
  <div class="hero-right">
    <img class="hero-img" src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&q=80" alt="Taller">
    <div class="hero-overlay"></div>
    <div class="hero-badge"><span>ABRE<br>HOY</span></div>
  </div>
</section>

<div class="marquee-wrap"><div class="marquee-inner">{% for i in range(2) %}<span>REPARACIÓN PROFESIONAL</span><span class="dot">◆</span><span>VENTA DE BICIS</span><span class="dot">◆</span><span>ACCESORIOS Y REPUESTOS</span><span class="dot">◆</span><span>AJUSTE Y TUNING</span><span class="dot">◆</span><span>SERVICIO TÉCNICO</span><span class="dot">◆</span><span>GARANTÍA EN TODOS LOS TRABAJOS</span><span class="dot">◆</span>{% endfor %}</div></div>

<section class="services" id="servicios">
  <div class="services-header"><div><div class="section-sub"><span class="line-h"></span>Lo que hacemos</div><h2 class="section-title">Servicios del taller</h2></div><a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="btn-secondary">Agendar cita →</a></div>
  <div class="services-grid">{% for s in servicios %}<div class="service-card"><span class="service-icon">{{ s.icono }}</span><div class="service-name">{{ s.nombre }}</div><div class="service-desc">{{ s.descripcion }}</div><div class="service-price">{{ s.precio }}</div></div>{% endfor %}</div>
</section>

<section class="catalog" id="catalogo">
  <div class="catalog-header"><div><div class="section-sub"><span class="line-h"></span>Lo que vendemos</div><h2 class="section-title">Catálogo</h2></div></div>
  <div class="filters">
    <button class="filter-btn active" data-filter="all">Todo</button>
    <button class="filter-btn" data-filter="bici">Bicicletas</button>
    <button class="filter-btn" data-filter="accesorio">Accesorios</button>
    <button class="filter-btn" data-filter="repuesto">Repuestos</button>
  </div>
  <div class="catalog-grid">
    {% for b in bicicletas %}<div class="product-card" data-cat="bici" data-img="{{ b.imagen }}" data-name="{{ b.modelo }}" data-cat-label="Bicicleta" data-desc="{{ b.descripcion }}" data-price="${{ '{:,.0f}'.format(b.precio) }} MXN" onclick="openModal(this)"><div class="prod-img"><img src="{{ b.imagen }}" alt="{{ b.modelo }}" loading="lazy">{% if b.badge %}<span class="prod-badge">{{ b.badge }}</span>{% endif %}</div><div class="prod-info"><div class="prod-cat">Bicicleta</div><div class="prod-name">{{ b.modelo }}</div><div class="prod-desc">{{ b.descripcion }}</div><div class="prod-footer"><div class="prod-price">${{ '{:,.0f}'.format(b.precio) }}<br><small>{{ b.talla }}</small></div><button class="btn-add">Ver más</button></div></div></div>{% endfor %}
    {% for a in accesorios %}<div class="product-card" data-cat="accesorio" data-img="{{ a.imagen }}" data-name="{{ a.nombre }}" data-cat-label="Accesorio" data-desc="{{ a.descripcion }}" data-price="${{ '{:,.0f}'.format(a.precio) }} MXN" onclick="openModal(this)"><div class="prod-img"><img src="{{ a.imagen }}" alt="{{ a.nombre }}" loading="lazy">{% if a.badge %}<span class="prod-badge">{{ a.badge }}</span>{% endif %}</div><div class="prod-info"><div class="prod-cat">Accesorio</div><div class="prod-name">{{ a.nombre }}</div><div class="prod-desc">{{ a.descripcion }}</div><div class="prod-footer"><div class="prod-price">${{ '{:,.0f}'.format(a.precio) }}<br><small>MXN</small></div><button class="btn-add">Ver más</button></div></div></div>{% endfor %}
    {% for r in repuestos %}<div class="product-card" data-cat="repuesto" data-img="{{ r.imagen }}" data-name="{{ r.nombre }}" data-cat-label="Repuesto" data-desc="{{ r.descripcion }}" data-price="${{ '{:,.0f}'.format(r.precio) }} MXN" onclick="openModal(this)"><div class="prod-img"><img src="{{ r.imagen }}" alt="{{ r.nombre }}" loading="lazy">{% if r.badge %}<span class="prod-badge">{{ r.badge }}</span>{% endif %}</div><div class="prod-info"><div class="prod-cat">Repuesto</div><div class="prod-name">{{ r.nombre }}</div><div class="prod-desc">{{ r.descripcion }}</div><div class="prod-footer"><div class="prod-price">${{ '{:,.0f}'.format(r.precio) }}<br><small>MXN</small></div><button class="btn-add">Ver más</button></div></div></div>{% endfor %}
  </div>
</section>

<section class="workshop" id="taller">
  <div class="workshop-left"><div class="section-sub">El taller</div><h2 class="section-title">Mecánicos<br>que aman<br>las bicis.</h2><p>Nuestro equipo tiene más de {{ info.anios }} años de experiencia reparando bicicletas.</p><p style="margin-top:.8rem">Garantía escrita y revisión de 30 días sin costo.</p><a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="workshop-btn">Reservar turno 🔧</a></div>
  <div class="workshop-right"><img src="https://images.unsplash.com/photo-1619818586372-5e77cfb7aeeb?w=800&q=80" alt="Taller"></div>
</section>

<div class="brands"><div class="brands-label">Marcas que trabajamos</div><div class="brands-row">{% for m in marcas %}<span class="brand-name">{{ m }}</span>{% endfor %}</div></div>

<section class="testimonials">
  <div class="testimonials-header"><div class="section-sub"><span class="line-h"></span>Lo que dicen</div><h2 class="section-title">Clientes felices</h2></div>
  <div class="reviews-grid">{% for r in resenas %}<div class="review-card"><div class="quote-mark">"</div><div class="review-stars">{% for i in range(r.estrellas) %}★{% endfor %}</div><p class="review-text">{{ r.texto }}</p><div class="review-author"><div class="avatar">{{ r.inicial }}</div><div><div class="author-name">{{ r.nombre }}</div><div class="author-date">{{ r.fecha }}</div></div></div></div>{% endfor %}</div>
</section>

<section class="contact" id="contacto">
  <div class="contact-info"><div class="section-sub"><span class="line-h"></span>Estamos aquí</div><h2 class="section-title">Contáctanos</h2><p>¿Quieres agendar una cita o saber más? Escríbenos o visítanos.</p>
    <div class="info-item"><div class="info-icon">📍</div><div><div class="info-label">Dirección</div><div class="info-value">{{ info.direccion }}</div></div></div>
    <div class="info-item"><div class="info-icon">📞</div><div><div class="info-label">Teléfono</div><div class="info-value">{{ info.telefono }}</div></div></div>
    <div class="info-item"><div class="info-icon">📧</div><div><div class="info-label">Email</div><div class="info-value">{{ info.email }}</div></div></div>
    <div class="info-item"><div class="info-icon">🕐</div><div><div class="info-label">Horarios</div>{% for h in info.horarios %}<div class="info-value">{{ h.dia }}: {{ h.hora }}</div>{% endfor %}</div></div>
    <div style="margin-top:1.5rem;border:1px solid #2a2a2a;overflow:hidden;height:220px;"><iframe width="100%" height="100%" frameborder="0" src="{{ info.maps_embed }}" style="filter:grayscale(80%) invert(90%) contrast(0.9);"></iframe></div>
  </div>
  <div><form class="contact-form" id="contactForm">
    <div class="form-row"><div class="form-field"><label class="form-label">Nombre</label><input type="text" class="form-input" id="fname" placeholder="Tu nombre" required></div><div class="form-field"><label class="form-label">Teléfono</label><input type="tel" class="form-input" id="fphone" placeholder="+52 55 ..."></div></div>
    <div class="form-field"><label class="form-label">Email</label><input type="email" class="form-input" id="femail" placeholder="tu@email.com" required></div>
    <div class="form-field"><label class="form-label">¿En qué podemos ayudarte?</label><select class="form-select" id="fservicio"><option value="">Selecciona una opción</option>{% for s in servicios %}<option>{{ s.nombre }}</option>{% endfor %}<option>Compra de bicicleta</option><option>Otro</option></select></div>
    <div class="form-field"><label class="form-label">Mensaje</label><textarea class="form-textarea" id="fmsg" placeholder="Cuéntanos más..."></textarea></div>
    <button type="submit" class="form-submit">Enviar mensaje →</button>
    <a href="https://wa.me/{{ info.whatsapp }}" target="_blank" class="whatsapp-btn">💬 Escribir por WhatsApp</a>
  </form></div>
</section>

<footer><div class="footer-top">
  <div class="footer-brand"><a href="#inicio" class="logo">{{ info.nombre[:4] }}<span>{{ info.nombre[4:] }}</span></a><p>{{ info.descripcion }}</p></div>
  <div class="footer-col"><h4>Servicios</h4><ul>{% for s in servicios %}<li><a href="#servicios">{{ s.nombre }}</a></li>{% endfor %}</ul></div>
  <div class="footer-col"><h4>Tienda</h4><ul><li><a href="#catalogo">Bicicletas</a></li><li><a href="#catalogo">Accesorios</a></li><li><a href="#catalogo">Repuestos</a></li></ul></div>
  <div class="footer-col"><h4>Contacto</h4><ul>{% if info.instagram %}<li><a href="{{ info.instagram }}" target="_blank">Instagram</a></li>{% endif %}{% if info.facebook %}<li><a href="{{ info.facebook }}" target="_blank">Facebook</a></li>{% endif %}<li><a href="https://wa.me/{{ info.whatsapp }}" target="_blank">WhatsApp</a></li><li><a href="/admin">⚙️ Admin</a></li></ul></div>
</div><div class="footer-bottom"><p>© 2025 {{ info.nombre }}. Todos los derechos reservados.</p><p>Hecho con <span class="orange">♥</span> para los amantes de la bicicleta</p></div></footer>

<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)"><div class="modal" onclick="event.stopPropagation()"><button class="modal-close" onclick="closeModal()">✕</button><img src="" alt="" class="modal-img" id="modalImg"><div class="modal-cat" id="modalCat"></div><div class="modal-title" id="modalTitle"></div><div class="modal-desc" id="modalDesc"></div><div class="modal-actions"><div class="modal-price" id="modalPrice"></div><a href="#contacto" class="btn-primary" onclick="closeModal()" style="text-decoration:none">Consultar →</a></div></div></div>
<div class="toast" id="toast"></div>

<script>
const cursor=document.getElementById('cursor');
document.addEventListener('mousemove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px';});
document.querySelectorAll('a,button,.product-card,.service-card,.filter-btn,.brand-name').forEach(el=>{el.addEventListener('mouseenter',()=>cursor.classList.add('hov'));el.addEventListener('mouseleave',()=>cursor.classList.remove('hov'));});
function toggleMenu(){document.getElementById('mobMenu').classList.toggle('open');}
document.querySelectorAll('.filter-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');const f=btn.dataset.filter;document.querySelectorAll('.product-card').forEach(c=>{c.classList.toggle('hidden',f!=='all'&&c.dataset.cat!==f);});});});
function openModal(card){document.getElementById('modalImg').src=card.dataset.img;document.getElementById('modalCat').textContent=card.dataset.catLabel;document.getElementById('modalTitle').textContent=card.dataset.name;document.getElementById('modalDesc').textContent=card.dataset.desc;document.getElementById('modalPrice').textContent=card.dataset.price;document.getElementById('modalOverlay').classList.add('open');}
function closeModal(e){if(!e||e.target===document.getElementById('modalOverlay'))document.getElementById('modalOverlay').classList.remove('open');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
document.getElementById('contactForm').addEventListener('submit',async function(e){e.preventDefault();const btn=this.querySelector('.form-submit');btn.textContent='Enviando...';btn.disabled=true;try{const res=await fetch('/contacto',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:document.getElementById('fname').value,telefono:document.getElementById('fphone').value,email:document.getElementById('femail').value,servicio:document.getElementById('fservicio').value,mensaje:document.getElementById('fmsg').value})});const data=await res.json();showToast(data.ok?'✅ Mensaje enviado. Te contactamos pronto.':'⚠️ Error al enviar.');if(data.ok)this.reset();}catch{showToast('⚠️ Error. Escríbenos por WhatsApp.');}btn.textContent='Enviar mensaje →';btn.disabled=false;});
function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),4000);}
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
        <html><body style="background:#222; color:white; padding:2rem; font-family:sans-serif;">
            <h1 style="color:#FF5500;">⚠️ Modo Diagnóstico</h1>
            <p>La página detectó un error al intentar dibujar el contenido. Mándale esto a tu programador:</p>
            <pre style="background:#111; padding:1rem; color:#ff9999; border-left: 4px solid red; overflow-x: auto;">{error_info}</pre>
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
    # CORRECCIÓN AQUÍ: Devolver la plantilla directamente para que Jinja no interfiera con Vue.
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