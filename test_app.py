import json
import unittest
from unittest.mock import patch, MagicMock
from app import app, sessions

class TestSocratesGemmaBackendMultiModule(unittest.TestCase):
    """
    Kelas pengujian unit (Unit Test) untuk integrasi multi-modul backend SOCRATES-GEMMA.
    Mencakup pengujian respons terbungkus {"status": "success", "data": ...}
    serta sinkronisasi data Peta Miskonsepsi dan Laporan Analitik.
    """

    def setUp(self):
        # Konfigurasi Flask test client
        self.app = app.test_client()
        self.app.testing = True
        # Reset data sesi in-memory sebelum setiap pengujian
        sessions.clear()

    @patch('app.client.models.generate_content')
    def test_chat_success_wrapped_format(self, mock_generate_content):
        """
        Menguji format respons terbungkus baru:
        - Harus mengembalikan {"status": "success", "data": {...}}
        - Memverifikasi keberadaan data miskonsepsi dan laporan analitik.
        """
        # Mock respons mentah dari Gemma
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "respons_teks": "Coba pikirin, gimana kalau persamaan kuadrat ini kita faktorkan dulu?",
            "current_level": 1,
            "status_persona": "kasual",
            "pemicu_aksi": {
                "buka_whiteboard": False,
                "topik_belajar": "Persamaan Kuadrat",
                "target_modul": "dashboard_utama"
            },
            "peta_miskonsepsi": {
                "node_error": "Kebingungan menentukan faktor pembuat nol",
                "kaitan_konsep": "Pemfaktoran Aljabar"
            },
            "laporan_analitik": {
                "ringkasan_progres": "Siswa sedang berdiskusi mengenai akar persamaan kuadrat.",
                "skor_effort": 85
            },
            "siswa_gagal_atau_minta_instan": False
        })
        mock_generate_content.return_value = mock_response

        payload = {
            "session_id": "session_test_456",
            "message": "Gimana cara cari akar dari x^2 - 5x + 6 = 0?"
        }

        response = self.app.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Parsing data respon
        res_data = json.loads(response.data.decode('utf-8'))
        
        # Verifikasi pembungkus respons
        self.assertEqual(res_data["status"], "success")
        self.assertIn("data", res_data)
        
        # Verifikasi data bersarang (nested) di dalam key 'data'
        inner_data = res_data["data"]
        self.assertEqual(inner_data["current_level"], 1)
        self.assertEqual(inner_data["status_persona"], "kasual")
        self.assertEqual(inner_data["pemicu_aksi"]["topik_belajar"], "Persamaan Kuadrat")
        self.assertEqual(inner_data["pemicu_aksi"]["target_modul"], "dashboard_utama")
        
        self.assertEqual(inner_data["peta_miskonsepsi"]["node_error"], "Kebingungan menentukan faktor pembuat nol")
        self.assertEqual(inner_data["laporan_analitik"]["skor_effort"], 85)
        
        # Pastikan data evaluasi internal dihapus
        self.assertNotIn("siswa_gagal_atau_minta_instan", inner_data)

    @patch('app.client.models.generate_content')
    def test_chat_failed_scaffolding_transitions(self, mock_generate_content):
        """
        Menguji transisi scaffolding level 2 ketika siswa mengirim keluhan/menyerah:
        - Memverifikasi aktivasi whiteboard visual dan deskripsi_visual.
        """
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "respons_teks": "Yuk, coba gambarin dulu bentuk kurvanya biar lebih kebayang di kepala.",
            "current_level": 2,
            "status_persona": "kasual",
            "pemicu_aksi": {
                "buka_whiteboard": True,
                "topik_belajar": "Parabola Kuadrat",
                "target_modul": "dashboard_utama",
                "deskripsi_visual": "Buat sumbu koordinat XY, lalu gambar parabola terbuka ke atas."
            },
            "peta_miskonsepsi": {
                "node_error": "Miskonsepsi arah lengkungan grafik",
                "kaitan_konsep": "Koefisien kuadratis"
            },
            "laporan_analitik": {
                "ringkasan_progres": "Siswa buntu secara visual pada arah parabola.",
                "skor_effort": 60
            },
            "siswa_gagal_atau_minta_instan": True
        })
        mock_generate_content.return_value = mock_response

        # Naikkan status attempts ke 1
        sessions["session_test_456"] = {"failed_attempts": 1}

        payload = {
            "session_id": "session_test_456",
            "message": "Nyerah deh, ga tau gimana gambarnya."
        }

        response = self.app.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.data.decode('utf-8'))
        
        inner_data = res_data["data"]
        self.assertEqual(inner_data["current_level"], 2)
        self.assertTrue(inner_data["pemicu_aksi"]["buka_whiteboard"])
        self.assertEqual(inner_data["pemicu_aksi"]["deskripsi_visual"], "Buat sumbu koordinat XY, lalu gambar parabola terbuka ke atas.")
        self.assertEqual(sessions["session_test_456"]["failed_attempts"], 2)

    def test_chat_missing_parameters(self):
        """
        Menguji error handling 400 jika parameter wajib tidak lengkap.
        """
        response = self.app.post(
            '/api/chat',
            data=json.dumps({"message": "Hanya pesan saja"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
