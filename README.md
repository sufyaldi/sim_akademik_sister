# SIM Akademik SISTER Integrator - Ekosistem Platform SIRITA( ) Sistem Informasi Universitas Terintegrasi 

Ekstensi resmi dari **Sistem Informasi Akademik (SIM Akademik)** yang dirancang secara khusus untuk menjadi jembatan integrasi *real-time* dua arah antara Odoo 18 dengan **SISTER (Sistem Informasi Sumber Daya Terintegrasi) Kemendikbudristek RI**.

---

##  Bagian dari Platform SIRITA
Sebagai bagian integral dari ekosistem **SIRITA** , modul ini menjunjung tinggi filosofi keprofesionalan pendidik dan mempermudah beban birokrasi kampus. Melalui otomatisasi sinkronisasi data SDM, dosen kini bisa lebih fokus pada proses belajar-mengajar dan penelitian karena rekam jejak mereka terjamin keutuhannya di dalam SISTER tanpa perlu *input* data berulang kali.

---

##  Fitur Unggulan

###  Multi-Role API Authentication & Sandbox
*   **Akses JWT Token**: Generator token *bearer* yang otomatis menangani pertukaran otorisasi melalui modul `sister.config`.
*   **Deteksi Institusi Cerdas**: Sinkronisasi Profil Perguruan Tinggi otomatis yang secara prediktif melacak UUID Kampus sebagai induk SISTER.

### 👥 Sinkronisasi Masif Portofolio Dosen (SDM)
Automatisasi penarikan referensi *database* yang langsung membentuk/memperbarui *record Employee* di Odoo:
*   **Update Profil & NIDN**: Tarik detail riwayat Nomor Induk, Status Pegawai, dan data primer Dosen/Tendik secara utuh.
*   **Tarik Massal**: Mampu menangani penarikan susunan ratusan data dosen PT sekaligus dalam 1 klik.

###  Sinkronisasi Tridharma Perguruan Tinggi
Komprehensi penuh atas riwayat Tridharma yang tertanam langsung di *tab* integrasi masing-masing profil dosen:
*   **Kinerja Pengajaran**: Riwayat kelas, semester aktif, SKS matkul, hingga rasio/jumlah mahasiswa KRS.
*   **Publikasi Ilmiah**: Rekaman jurnal/publikasi lengkap dengan klasifikasi sinta, kuartil, jenis karya, hingga tanggal.
*   **Pengabdian Masyarakat**: Data Litabmas dan kepanitiaan dosen per semester.

###  Sinkronisasi Kepegawaian Akademik
Sistem kepangkatan yang terstruktur untuk manajemen Payroll/Honorarium di masa mendatang:
*   **Jabatan Fungsional**: Identifikasi otomatis SK Asisten Ahli hingga Guru Besar.
*   **Kepangkatan**: Rekaman daftar pangkat/golongan dari SISTER.
*   **Pendidikan Formal**: Pelacakan ijazah (Linearitas Jenjang PT).
*   **Sertifikasi (Serdos)**: Bukti kompetensi profesional untuk pelaporan kelayakan tunjangan akademik.

###  Otomatisasi Background Job (Crons)
*   Menjalankan penarikan *Tridharma* & Kepegawaian ratusan dosen tanpa intervensi manual setiap malam jam 01:00 am WIB.
*   Sistem antrean *Graceful* yang tidak membatalkan proses keseluruhan jika terjadi *timeout* di sebagian pengguna.

---

##  Instalasi

1. Clone repositori ini menjadi *addon* pendamping dari `sim_akademik` utama Anda.
2. Pastikan dependensi berikut telah terpasang:
   * `base`
   * `hr`
   * `sim_akademik`
   * Server memiliki kapabilitas *pip install requests* 
3. Perbarui *App List* di environment Odoo Anda.
4. Pasang modul `sim_akademik_sister`.

##  Cara Penggunaan Cepat

1. Buka Odoo, login sebagai Administrator.
2. Masuk ke menu **SISTER API** (biasanya berada pada konfigurasi SIM Akademik).
3. Masukkan `Username`, `Password`, dan `ID Pengguna` yang di-generate dari server *SISTER Cloud / Sandbox*.
4. Klik **Generate Token** lalu klik **Tarik Referensi PT**.
5. Kunjungi salah satu *Employee*, tekan **Sync Profil SISTER** untuk memperbarui datanya secara tunggal, atau hidupkan *Scheduled Actions* untuk menariknya massal secara malam hari.

##  Persyaratan Sistem
*   **Versi Odoo**: 18.x (Community atau Enterprise)
*   **Ketergantungan External**: Modul `sim_akademik`.
*   **Versi Python**: 3.10+
*   **Lib**: `requests` Python library (`python3 -m pip install requests`).

##  Lisensi
Modul ini dilisensikan di bawah **GNU General Public License v3.0**.

---
*Dikembangkan dengan ❤️ untuk masa depan pendidikan tinggi Indonesia yang lebih tangguh.*
