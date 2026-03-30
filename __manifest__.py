# -*- coding: utf-8 -*-
{
    'name': 'SIM Akademik - SISTER Kemendikbud Sync',
    'version': '1.0',
    'category': 'Academic',
    'summary': 'Sinkronisasi Data Dosen, Pengajaran, dan Riset dengan SISTER Cloud',
    'description': """
        SIM Akademik SISTER Integrator - Ekosistem Platform SIRITA
        ==========================================================
        Modul independen penghubung Platform SIRITA (Sistem Informasi Cerdas Cita) dengan REST API SISTER (Sistem Informasi Sumber Daya Terintegrasi) Kemendikbudristek RI.

        Fitur Utama:
        - Sinkronisasi Profil SDM dan NIDN Server-to-Server
        - Kinerja Pengajaran & Mahasiswa Bimbingan
        - Riwayat Publikasi Ilmiah & Pengabdian Masyarakat
        - Sertifikasi Dosen, Pendidikan Formal, dan Jabatan Fungsional
        - Automated Cron Job Engine (Sinkronisasi Massal)
    """,
    'author': 'SIRITA Platform',
    'website': 'https://sirita.id',
    'depends': ['base', 'hr', 'sim_akademik', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/sister_config_views.xml',
        'views/sister_sync_log_views.xml',
        'views/hr_employee_sister_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'GPL-3',
}
