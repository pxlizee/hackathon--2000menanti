# Educeria - Orion Class (Socrates-Gemma Learning Buddy)

**Educeria (Orion Class)** adalah aplikasi web pembelajaran sokratik berbasis AI yang dirancang interaktif dan ramah anak untuk membantu mempelajari konsep Matematika, Sains, dan Bahasa secara menyenangkan. Aplikasi ini menggabungkan antarmuka Single Page Application (SPA) yang dinamis dengan pemrosesan bahasa alami dari Google Gemini (Gemma-4-27b-it).

---

## 🚀 Fitur Utama

1. **Alur Masuk Petualangan (Interactive Auth)**:
   * Login portal interaktif bertema petualangan ruang angkasa dengan animasi loading 1.5 detik.
2. **Papan Tulis Kolaboratif (Collaborative Drawing Whiteboard)**:
   * Canvas gambar interaktif untuk corat-coret rumus atau bagan. Mendukung interaksi mouse & multi-touch pada layar sentuh.
   * Terbuka otomatis apabila Socrates AI memberikan panduan visual (`buka_whiteboard = true`).
3. **Peta Kognitif Dinamis (Cognitive Graph Map)**:
   * Node kognitif visual yang melacak miskonsepsi secara real-time. Jika miskonsepsi terdeteksi, node bermasalah akan disorot warna merah dengan notifikasi visual agar anak kembali berdiskusi dengan AI.
4. **Status Belajar Terkoneksi**:
   * Melacak progres pemahaman, waktu belajar secara real-time, dan evaluasi motivasi dari Socrates AI.
5. **Dukungan Suara Penuh (Voice STT & TTS)**:
   * **Voice Input**: Mengubah ucapan suara anak menjadi teks chat secara instan (Speech-to-Text).
   * **Voice Output**: Membacakan jawaban teks Socrates AI secara lantang dengan bahasa Indonesia yang natural (Text-to-Speech).
6. **Laporan & Perpustakaan**:
   * Laporan perkembangan anak berbasis statistik usaha (*Effort Score*) harian.
   * Katalog modul pembelajaran dengan sistem penyaringan (Matematika, Sains, Bahasa).

---

## 🛠️ Stack Teknologi

### **Frontend**
* **HTML5 & Tailwind CSS**: Kerangka semantik dengan token warna premium ramah anak sesuai panduan `DESIGN.md`.
* **HTML5 Canvas API**: Pembuatan papan coretan responsif bebas glitch.
* **Web Speech API**: Modul `SpeechRecognition` (STT) dan `SpeechSynthesis` (TTS) native browser.
* **Vanilla JavaScript (ES6)**: Router SPA klien, state manager, dan visualisasi chart radial SVG.

### **Backend**
* **Python (Flask)**: Server mikro API perantara klien dan model AI.
* **SQLite (SQLite3)**: Database lokal penyimpan log percakapan siswa (`chat_history`) agar memori AI tetap berkesinambungan.
* **Google GenAI SDK**: Integrasi model Socratic Gemma (`gemma-4-27b-it` / `gemma-4-31b-it`) untuk merumuskan respon scaffolding terstruktur.

---

## 📦 Panduan Instalasi & Cara Menjalankan

### **Prasyarat**
Pastikan Anda sudah menginstal **Python 3.10+** pada sistem Anda.

### **1. Kloning Repositori**
```bash
git clone https://github.com/username/hackathon.git
cd hackathon
```

### **2. Setup Virtual Environment & Pasang Dependensi**
```bash
# Membuat virtual environment
python3 -m venv venv

# Mengaktifkan virtual environment
# Pada macOS/Linux:
source venv/bin/activate
# Pada Windows:
.\venv\Scripts\activate

# Memasang modul dependensi Python
pip install -r requirements.txt
```

### **3. Konfigurasi API Key Gemini**
Dapatkan API Key Gemini Anda dari Google AI Studio, kemudian atur sebagai environment variable:
```bash
# macOS/Linux
export GEMINI_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set GEMINI_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"
```

### **4. Jalankan Flask Backend Server**
```bash
python app.py
```
Server akan berjalan di alamat `http://localhost:5000`.

### **5. Akses Aplikasi Web**
Cukup buka file `index.html` langsung menggunakan browser favorit Anda (rekomendasi: Google Chrome untuk performa Speech Recognition terbaik), atau jalankan local server seperti Live Server pada VS Code.

---

## 🔑 Kredensial Akses Mockup
Untuk masuk ke aplikasi web, gunakan masukan nama dan sandi bebas (simulasi login):
* **Nama Pengguna**: `budi` atau apa saja
* **Kata Sandi**: `bebas` atau apa saja

---
*Belajar jadi petualangan seru bersama **Orion Class**!* 🌟
