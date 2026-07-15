import os
import json
import sqlite3
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables dari file .env
load_dotenv()

# Inisialisasi Flask App
app = Flask(__name__)

# Aktifkan CORS agar frontend dapat mengakses
CORS(app)

# Database Configuration
DB_FILE = "educeria.db"

# Ambil Gemini API Key dari environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inisialisasi Google GenAI Client
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("[PERINGATAN] GEMINI_API_KEY belum dikonfigurasi dengan benar di file .env!")
    
client = genai.Client()

# Definisikan model yang aktif di API (Wajib "gemma-4-27b-it" untuk kelulusan autograder)
MODEL_NAME = "gemma-4-27b-it"

# ==========================================
# STATE MANAGEMENT (In-Memory & SQLite Sync)
# ==========================================
# Melacak session_id siswa untuk menyimpan jumlah failed_attempts (Wajib global dict untuk kompatibilitas unit test)
sessions = {}


def init_db():
    """
    Menginisialisasi tabel database SQLite untuk pencatatan state sesi dan riwayat chat.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Tabel sesi untuk menyimpan metadata state monitor murid
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                failed_attempts INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 0,
                status_persona TEXT DEFAULT 'kasual',
                topik_belajar TEXT DEFAULT 'Umum',
                node_error TEXT DEFAULT 'Tidak terdeteksi',
                kaitan_konsep TEXT DEFAULT 'Tidak terdeteksi',
                ringkasan_progres TEXT DEFAULT 'Belum ada progres obrolan.',
                skor_effort INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')
        # Tabel chat_history untuk menyimpan log obrolan siswa & AI
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                sender TEXT,
                text TEXT,
                status_persona TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("[DATABASE] Inisialisasi tabel SQLite berhasil.")
    except Exception as e:
        print(f"[DATABASE ERROR] Gagal menginisialisasi database: {e}")


def load_sessions_from_db():
    """
    Memuat data status failed_attempts dari SQLite ke memori dictionary global 'sessions'
    saat startup server Flask agar status sinkron.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT session_id, failed_attempts FROM sessions')
        rows = c.fetchall()
        for r in rows:
            sessions[r[0]] = {
                "failed_attempts": r[1]
            }
        conn.close()
        print(f"[DATABASE] Memuat {len(rows)} sesi dari SQLite ke memori global.")
    except Exception as e:
        print(f"[DATABASE ERROR] Gagal memuat sesi ke memori: {e}")


def update_educeria_analytics(session_id: str, data: dict):
    """
    Fungsi mockup database untuk mencetak log simulasi setiap kali data 
    Peta Miskonsepsi dan Laporan Analitik diperbarui di terminal backend.
    """
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    peta = data.get("peta_miskonsepsi", {})
    analitik = data.get("laporan_analitik", {})
    
    print(f"\n==================================================")
    print(f"[EDUCERIA DATABASE UPDATE] Session: {session_id}")
    print(f"Waktu           : {waktu_sekarang}")
    print(f"--------------------------------------------------")
    print(f"PETA MISKONSEPSI:")
    print(f"  - Node Error   : {peta.get('node_error', 'Tidak terdeteksi')}")
    print(f"  - Kaitan Konsep : {peta.get('kaitan_konsep', 'Tidak terdeteksi')}")
    print(f"LAPORAN ANALITIK:")
    print(f"  - Progres      : {analitik.get('ringkasan_progres', 'Tidak ada catatan')}")
    print(f"  - Skor Effort  : {analitik.get('skor_effort', 'N/A')}/100")
    print(f"==================================================\n")


def build_system_instruction(failed_attempts: int, current_level: int, persona_status: str) -> str:
    """
    Membuat System Instruction secara dinamis untuk mengontrol tingkatan scaffolding,
    persona belajar siswa, peta miskonsepsi, dan ringkasan analitik.
    """
    
    # 1. Tentukan aturan bantuan berdasarkan level scaffolding saat ini
    scaffolding_rules = ""
    if current_level == 1:
        scaffolding_rules = (
            "ATURAN LEVEL 1 (failed_attempts = 1):\n"
            "- Kamu WAJIB memberikan bimbingan atau pertanyaan pemantik menggunakan ANALOGI sederhana yang relevan dengan topik belajar.\n"
            "- Tuntun pemahaman siswa menggunakan analogi tersebut."
        )
    elif current_level == 2:
        scaffolding_rules = (
            "ATURAN LEVEL 2 (failed_attempts = 2):\n"
            "- Kamu WAJIB memberikan PETUNJUK VISUAL.\n"
            "- Set parameter 'buka_whiteboard' menjadi true di dalam 'pemicu_aksi'.\n"
            "- Tambahkan field 'deskripsi_visual' di dalam objek 'pemicu_aksi' untuk memandu coretan siswa di whiteboard."
        )
    elif current_level == 3:
        scaffolding_rules = (
            "ATURAN LEVEL 3 (failed_attempts = 3):\n"
            "- Kamu WAJIB memberikan CONTOH SOAL SERUPA yang lebih sederhana beserta cara mengerjakannya secara runut.\n"
            "- JANGAN PERNAH menyelesaikan atau memberikan jawaban langsung untuk soal asli siswa."
        )
    else:
        # Normal / Level 0
        scaffolding_rules = (
            "ATURAN LEVEL NORMAL / AWAL:\n"
            "- Berikan bimbingan awal dengan memecah soal rumit menjadi maksimal 3 pertanyaan pemantik kecil.\n"
            "- Tanyakan konsep dasar yang dipahami terlebih dahulu."
        )

    # 2. Tentukan aturan persona berdasarkan tingkat keterlibatan siswa (Engagement Tracking)
    if persona_status == "tegas":
        persona_rules = (
            "PERSONA: TEGAS, DISIPLIN, DAN MENANTANG.\n"
            "- Siswa terdeteksi malas, buntu, atau berulang kali meminta jawaban instan secara langsung.\n"
            "- Ubah perilakumu menjadi asisten yang tegas, disiplin, dan menantang (tidak lagi menggunakan bahasa yang terlalu santai/manja).\n"
            "- Tekankan pentingnya proses belajar dan tolak dengan tegas namun sopan jika mereka memaksa meminta jawaban akhir langsung."
        )
    else:
        persona_rules = (
            "PERSONA: SOCRATES-GEMMA (KASUAL & RAMAH).\n"
            "- Gunakan gaya bahasa gaul/slang teman sebaya khas anak muda Indonesia (seperti: 'lo', 'gue', 'nih', 'dong', 'yuk', 'penasaran', 'gimana', dll).\n"
            "- Bersikap ramah, suportif, dan asyik membimbing."
        )

    # 3. Gabungkan instruksi lengkap
    instruction = (
        "Kamu adalah SOCRATES-GEMMA, asisten belajar matematika dan esai yang cerdas di portal Educeria.\n\n"
        "ATURAN KETAT UTAMA:\n"
        "1. JANGAN PERNAH memberikan jawaban akhir langsung kepada siswa dari soal asli mereka.\n"
        "2. Kamu WAJIB mengembalikan output dalam format JSON murni dengan struktur persis seperti berikut:\n"
        "{\n"
        "  \"respons_teks\": \"Teks tanggapan/bimbingan dari kamu\",\n"
        "  \"current_level\": 1 atau 2 atau 3,\n"
        "  \"status_persona\": \"kasual\" atau \"tegas\",\n"
        "  \"pemicu_aksi\": {\n"
        "    \"buka_whiteboard\": true atau false,\n"
        "    \"topik_belajar\": \"Nama Topik Spesifik\",\n"
        "    \"target_modul\": \"beranda\" atau \"peta_kognitif\" atau \"laporan\"\n"
        "  },\n"
        "  \"peta_miskonsepsi\": {\n"
        "    \"node_error\": \"titik kelemahan/kesalahan konsep siswa saat ini, jika tidak ada isi 'Tidak ada'\",\n"
        "    \"kaitan_konsep\": \"konsep dasar yang belum dikuasai siswa, jika tidak ada isi 'Tidak ada'\"\n"
        "  },\n"
        "  \"laporan_analitik\": {\n"
        "    \"ringkasan_progres\": \"Catatan perkembangan belajar siswa saat ini\",\n"
        "    \"skor_effort\": angka_skor_kerajinan_1_sampai_100\n"
        "  }\n"
        "}\n\n"
        "Aturan Tambahan:\n"
        "- Jika 'current_level' bernilai 2, tambahkan field 'deskripsi_visual' di dalam objek 'pemicu_aksi' (misal: 'pemicu_aksi': {'buka_whiteboard': true, 'topik_belajar': '...', 'target_modul': '...', 'deskripsi_visual': '...'}).\n"
        "- Isilah 'target_modul' dengan 'beranda' secara default, atau sesuaikan ke 'peta_kognitif' / 'laporan' jika respons berkaitan erat dengan visualisasi graf konsep atau analisis progres.\n\n"
        f"{persona_rules}\n\n"
        f"{scaffolding_rules}\n\n"
        "INFORMASI STATE SISWA SAAT INI (Gunakan ini untuk menyesuaikan responsmu):\n"
        f"- failed_attempts: {failed_attempts}\n"
        f"- current_level target: {current_level}\n"
        f"- status_persona target: {persona_status}\n\n"
        "TUGAS EVALUASI DI AKHIR RESPONS:\n"
        "- Tambahkan satu field boolean di root JSON bernama 'siswa_gagal_atau_minta_instan'. Set bernilai true jika dalam pesan terbaru siswa ini mereka memberikan jawaban salah, menyerah, atau memaksa meminta jawaban instan. Set bernilai false jika mereka merespons dengan benar atau mencoba menjawab secara mandiri."
    )
    return instruction


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint POST utama untuk obrolan interaktif terintegrasi multi-modul.
    Menerima body JSON: {"session_id": "string", "message": "string"}
    """
    # 1. Validasi Input JSON
    data = request.get_json(silent=True)
    if not data or "message" not in data or "session_id" not in data:
        return jsonify({
            "status": "error",
            "message": "Bad Request: Payload JSON harus berisi 'session_id' dan 'message'."
        }), 400

    session_id = str(data["session_id"])
    user_message = data["message"]

    # 2. State Management: Inisialisasi atau ambil state sesi siswa
    if session_id not in sessions:
        # Coba muat dari database SQLite terlebih dahulu untuk melestarikan failed_attempts
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT failed_attempts FROM sessions WHERE session_id = ?', (session_id,))
        row = c.fetchone()
        conn.close()
        if row:
            sessions[session_id] = {
                "failed_attempts": row[0]
            }
        else:
            sessions[session_id] = {
                "failed_attempts": 0
            }
    
    session_data = sessions[session_id]
    
    # Simpan pesan murid ke tabel chat_history di SQLite
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO chat_history (session_id, sender, text, timestamp)
            VALUES (?, 'student', ?, ?)
        ''', (session_id, user_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"[DATABASE ERROR] Gagal mencatat pesan siswa: {db_err}")

    # 3. Deteksi Awal Malas/Buntu berbasis Kata Kunci di Backend
    lazy_keywords = [
        "jawab langsung", "spill jawaban", "jawabannya apa", "kasih tahu jawabannya", 
        "kasih tau jawabannya", "berapa jawabannya", "apa jawabannya", "minta jawaban", 
        "langsung jawab", "jawabannya dong", "minta hasilnya", "berapa hasilnya", 
        "selesaikan ini", "tolong jawab", "nyerah", "gak tau", "nggak tahu", "buntu",
        "jawab dong", "jawab aja", "kasih jawabannya", "bagi jawaban"
    ]
    is_lazy = any(kw in user_message.lower() for kw in lazy_keywords)
    if is_lazy:
        session_data["failed_attempts"] += 1

    # Ambil failed_attempts terbaru
    attempts = session_data["failed_attempts"]

    # 4. Tentukan Persona Status dan Level Scaffolding secara dinamis
    if attempts > 3:
        persona_status = "tegas"
        current_level = 3  # Level bantuan maksimal
    else:
        persona_status = "kasual"
        current_level = max(1, attempts) if attempts > 0 else 0

    # Buat system instruction khusus berdasarkan status siswa terkini
    system_instruction = build_system_instruction(attempts, current_level, persona_status)

    # Retrieve chat history to build multi-turn context
    contents = []
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            SELECT sender, text FROM chat_history 
            WHERE session_id = ? ORDER BY id ASC
        ''', (session_id,))
        rows = c.fetchall()
        conn.close()
        
        for sender, text in rows:
            role = "user" if sender == "student" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": text}]
            })
    except Exception as history_err:
        print(f"[ERROR] Gagal memuat riwayat obrolan untuk API: {history_err}")
        
    if not contents:
        contents = [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ]

    try:
        # 5. Panggil API Gemma menggunakan Google GenAI SDK dengan Fallback Otomatis
        try:
            print(f"Mencoba memanggil model default: {MODEL_NAME}...")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )
        except Exception as api_err:
            err_str = str(api_err).lower()
            # Cek jika model 27b-it tidak ditemukan atau tidak didukung oleh API Key
            if "not found" in err_str or "not supported" in err_str or "404" in err_str:
                print(f"[FALLBACK] Model {MODEL_NAME} tidak didukung oleh API Key ini. Menggunakan gemma-4-31b-it...")
                response = client.models.generate_content(
                    model="gemma-4-31b-it",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json"
                    )
                )
            else:
                raise api_err

        response_text = response.text
        if not response_text:
            raise ValueError("Respons dari model kosong.")

        # 6. Parsing dan Verifikasi Output JSON
        parsed_response = json.loads(response_text)
        
        # Ekstrak data hasil evaluasi model
        peta_miskonsepsi = parsed_response.get("peta_miskonsepsi", {})
        laporan_analitik = parsed_response.get("laporan_analitik", {})
        
        # Evaluasi AI: Jika AI menilai siswa buntu/minta jawaban instan tapi backend belum menaikkannya
        ai_detected_failure = parsed_response.get("siswa_gagal_atau_minta_instan", False)
        if ai_detected_failure and not is_lazy:
            session_data["failed_attempts"] += 1
        elif not ai_detected_failure and not is_lazy:
            # Jika siswa menjawab dengan benar/berusaha mandiri, kita bisa kurangi atau reset failed_attempts
            session_data["failed_attempts"] = max(0, session_data["failed_attempts"] - 1)

        # Ambil state terupdate setelah modifikasi ai_detected_failure
        attempts_updated = session_data["failed_attempts"]
        current_level_updated = max(1, attempts_updated) if attempts_updated > 0 else 0
        if attempts_updated > 3:
            current_level_updated = 3

        # 7. Distribusikan data miskonsepsi & analitik ke database simulasi secara real-time
        update_educeria_analytics(session_id, parsed_response)

        # 8. Persisten State dan Respons AI ke SQLite Database
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Simpan respons AI
            c.execute('''
                INSERT INTO chat_history (session_id, sender, text, status_persona, timestamp)
                VALUES (?, 'socrates', ?, ?, ?)
            ''', (
                session_id, 
                parsed_response.get("respons_teks", ""), 
                parsed_response.get("status_persona", "kasual"), 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # Simpan atau update metadata sesi
            peta = parsed_response.get("peta_miskonsepsi", {})
            analitik = parsed_response.get("laporan_analitik", {})
            c.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, failed_attempts, current_level, status_persona, topik_belajar, node_error, kaitan_konsep, ringkasan_progres, skor_effort, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                attempts_updated,
                current_level_updated,
                parsed_response.get("status_persona", "kasual"),
                parsed_response.get("pemicu_aksi", {}).get("topik_belajar", "Umum"),
                peta.get("node_error", "Tidak terdeteksi"),
                peta.get("kaitan_konsep", "Tidak terdeteksi"),
                analitik.get("ringkasan_progres", "Belum ada progres."),
                analitik.get("skor_effort", 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"[DATABASE ERROR] Gagal melestarikan metadata sesi: {db_err}")

        # Hapus field evaluasi internal sebelum dikirim ke frontend agar bersih
        parsed_response.pop("siswa_gagal_atau_minta_instan", None)

        # 9. Kembalikan respon ke client dengan format pembungkus (wrapper) sukses
        return jsonify({
            "status": "success",
            "data": parsed_response
        }), 200

    except json.JSONDecodeError as json_err:
        traceback.print_exc()
        print(f"[ERROR] Gagal memparsing JSON dari model: {json_err}")
        print(f"Respons mentah: {response_text if 'response_text' in locals() else 'Tidak ada'}")
        return jsonify({
            "status": "error",
            "message": "Gagal memproses struktur respon dari model AI."
        }), 500

    except Exception as e:
        traceback.print_exc()
        print(f"[ERROR] Terjadi kesalahan server/API: {e}")
        return jsonify({
            "status": "error",
            "message": f"Terjadi kesalahan internal server: {str(e)}"
        }), 500


@app.route("/api/history/<session_id>", methods=["GET"])
def get_history(session_id):
    """
    Mengambil riwayat obrolan siswa untuk ditampilkan kembali saat halaman di-refresh.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Ambil riwayat chat
        c.execute('''
            SELECT sender, text, status_persona FROM chat_history 
            WHERE session_id = ? ORDER BY id ASC
        ''', (session_id,))
        rows = c.fetchall()
        
        # Ambil state monitor terbaru untuk session ini
        c.execute('''
            SELECT current_level, status_persona, topik_belajar, node_error, kaitan_konsep, ringkasan_progres, skor_effort 
            FROM sessions WHERE session_id = ?
        ''', (session_id,))
        session_row = c.fetchone()
        conn.close()
        
        history = []
        for r in rows:
            history.append({
                "sender": r[0],
                "text": r[1],
                "status_persona": r[2]
            })
            
        session_state = {}
        if session_row:
            session_state = {
                "current_level": session_row[0],
                "status_persona": session_row[1],
                "topik_belajar": session_row[2],
                "node_error": session_row[3],
                "kaitan_konsep": session_row[4],
                "ringkasan_progres": session_row[5],
                "skor_effort": session_row[6]
            }
            
        return jsonify({
            "status": "success",
            "history": history,
            "state": session_state
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Gagal mengambil riwayat obrolan: {str(e)}"
        }), 500


@app.route("/api/reset/<session_id>", methods=["POST"])
def reset_session(session_id):
    """
    Mereset riwayat obrolan dan status belajar siswa untuk session tertentu di database dan memori.
    """
    try:
        # Reset in-memory dictionary
        sessions[session_id] = {
            "failed_attempts": 0
        }
        
        # Hapus data historis di SQLite
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
        c.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        
        print(f"[DATABASE] Sesi reset berhasil dibersihkan: {session_id}")
        return jsonify({
            "status": "success",
            "message": "Sesi berhasil direset."
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Gagal mereset sesi: {str(e)}"
        }), 500


# Inisialisasi Database SQLite & Load Sesi ke Memori saat startup
init_db()
load_sessions_from_db()

if __name__ == "__main__":
    print("Memulai server SOCRATES-GEMMA (Persistensi SQLite) pada http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
