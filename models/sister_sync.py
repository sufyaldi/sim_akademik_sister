# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, _

class SisterConfig(models.Model):
    _name = 'sister.config'
    _description = 'Konfigurasi API SISTER Cloud'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama Konfigurasi', required=True, default='SISTER Cloud Production')
    base_url = fields.Char(string='Base URL API', required=True, placeholder='https://sister-api.kemdikbud.go.id/ws.php/1.0')
    api_token = fields.Char(string='API Token (Ter-generate)', readonly=True, help="Otomatis terisi setelah menekan tombol Generate Token (Login)")
    
        # Tambahan Field Identitas Institusi
    id_pt = fields.Char(string='ID Perguruan Tinggi (SISTER)', help="Otomatis diisi, atau ketik secara mekanik (Manual) format UUID jika API membalas {}")
    nama_pt = fields.Char(string='Nama Perguruan Tinggi')

    username = fields.Char(string='Username SISTER', required=True)
    password = fields.Char(string='Password SISTER', required=True)
    id_pengguna = fields.Char(string='ID Pengguna (UUID SISTER)', required=True, help='ID Institusi/Pengguna untuk Web Service (Format UUID)')
    
    is_active = fields.Boolean(string='Aktif', default=True)
    last_sync_time = fields.Datetime(string='Waktu Sinkron Terakhir', readonly=True)

    @api.model
    def action_cron_sync_all_sister_data(self):
        """Metode Cron untuk Sinkronisasi Massal Semua Dosen (Backgorund Job)"""
        config = self.search([('is_active', '=', True)], limit=1)
        if not config:
            return False
            
        # Refresh token agar aman ditarik untuk ribuan data
        try:
            config.action_get_token()
        except Exception:
            pass
            
        employees = self.env['hr.employee'].search([('sister_id', '!=', False)])
        total = len(employees)
        
        success = 0
        failed = 0
        
        # Eksekusi metode sinkron per dosen
        for emp in employees:
            try:
                emp.action_sync_to_sister()
                emp.action_sync_pengajaran_to_sister()
                emp.action_sync_publikasi_pengabdian_to_sister()
                emp.action_sync_kepegawaian_to_sister()
                success += 1
            except Exception:
                failed += 1
                
        config.last_sync_time = fields.Datetime.now()
        
        self.env['sister.sync.log'].create({
            'name': 'Cron Job: Mass Sync Tridharma',
            'model_name': 'sister.config',
            'res_id': config.id,
            'status': 'success' if failed == 0 else 'warning',
            'message': f"Otomatisasi Cron Job selesai.\nHasil eksekusi {total} Dosen:\nSukses: {success}\nGagal: {failed}",
        })
        return True

    def action_test_connection(self):
        """Uji koneksi ke API SISTER dan simpan respons di log."""
        self.ensure_one()
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Menguji koneksi dengan metode GET ke base_url terlebih dahulu
            response = requests.get(self.base_url, headers=headers, timeout=10)
            
            # Kita anggap berhasil terhubung jika respon API bukanlah Timeout/Network Error
            # Walaupun status 401/403 (Unauthorized), itu berarti 'server SISTER berhasil merespons'.
            is_connected = response.status_code in [200, 401, 403, 404]
            status = 'success' if is_connected else 'failed'
            
            pesan = f"Status Code: {response.status_code}\nResponse: {response.text[:500]}"
            
            # Catat hasil ke log
            self.env['sister.sync.log'].create({
                'name': 'Test Connection API SISTER',
                'model_name': 'sister.config',
                'res_id': self.id,
                'status': status,
                'message': pesan,
            })
            
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Uji Koneksi Berhasil' if is_connected else 'Uji Koneksi Gagal',
                    'message': f'Server SISTER merespons dengan status {response.status_code}. Cek menu Sync Logs untuk detailnya.',
                    'type': 'success' if is_connected else 'danger',
                    'sticky': False,
                }
            }
            return notification

        except Exception as e:
            error_msg = f"Koneksi Timeout / Terputus: {str(e)}"
            self.env['sister.sync.log'].create({
                'name': 'Test Connection API SISTER',
                'model_name': 'sister.config',
                'res_id': self.id,
                'status': 'failed',
                'message': error_msg,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error Jaringan',
                    'message': 'Gagal menjangkau URL API SISTER!',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def action_get_token(self):
        """Mendapatkan token Bearer baru (Login API) dari SISTER."""
        self.ensure_one()
        url = f"{self.base_url.rstrip('/')}/authorize"
        payload = {
            "username": self.username,
            "password": self.password,
            "id_pengguna": self.id_pengguna
        }
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                
                if token:
                    self.api_token = token
                    self.env['sister.sync.log'].create({
                        'name': 'Generate Token API SISTER',
                        'model_name': 'sister.config',
                        'res_id': self.id,
                        'status': 'success',
                        'message': 'Otorisasi Berhasil. Token baru telah diterbitkan (Berlaku 60 Menit).',
                    })
                    
                    # OTO-SINKRONISASI: Langsung tarik data Kampus tanpa disuruh
                    try:
                        self.action_get_referensi_pt()
                    except Exception:
                        pass # Biarkan tombol manual menangani jika ini gagal karena timeout sementara

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Token Terbit!',
                            'message': 'Token JWT berhasil didapatkan dari server SISTER.',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            
            # Jika respon di luar Ekspektasi / Gagal
            self.env['sister.sync.log'].create({
                'name': 'Generate Token API SISTER',
                'model_name': 'sister.config',
                'status': 'failed',
                'message': f"Status Code: {response.status_code}\nResponse: {response.text[:500]}",
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Gagal Mendapatkan Token',
                    'message': 'Kredensial ditolak atau URL salah. Cek Sync Logs.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        except Exception as e:
            return self._handle_network_error('Generate Token (Login)', e)

    def action_get_referensi_pt(self):
        """Menarik ID Perguruan Tinggi dari SISTER."""
        self.ensure_one()
        url = f"{self.base_url.rstrip('/')}/referensi/profil_pt"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Karena endpoint profil_pt mengembalikan data array atau dict
                pt_data = None
                if isinstance(data, list) and len(data) > 0:
                    pt_data = data[0]
                elif isinstance(data, dict) and data:
                    pt_data = data
                    
                if pt_data:
                    self.id_pt = pt_data.get('id') or self.id_pengguna
                    self.nama_pt = pt_data.get('nama_perguruan_tinggi') or "PT (Unknown Name)"
                    
                    self.env['sister.sync.log'].create({
                        'name': 'Tarik Referensi PT',
                        'model_name': 'sister.config',
                        'res_id': self.id,
                        'status': 'success',
                        'message': f"ID PT berhasil ditarik: {self.id_pt} - {self.nama_pt}",
                    })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Berhasil!',
                            'message': f'Dikenali sebagai: {self.nama_pt}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                    
                else:
                    # Endpoint PT mungkin kosong di sandbox atau token khusus
                    # Kita set ID PT otomatis menggunakan ID Pengguna
                    self.id_pt = self.id_pengguna
                    self.nama_pt = "Institusi Default (Cek dari id_pengguna)"
                    
                    self.env['sister.sync.log'].create({
                        'name': 'Tarik Referensi PT',
                        'model_name': 'sister.config',
                        'res_id': self.id,
                        'status': 'warning',
                        'message': f"Data PT kosong dari endpoint. Otomatis mengisi id_pt dari id_pengguna.",
                    })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Berhasil (dengan Peringatan)',
                            'message': 'SISTER tidak merujuk Nama PT. Kita gunakan UUID dari ID Pengguna default.',
                            'type': 'warning',
                            'sticky': False,
                        }
                    }
                    
            # Jika Token kedaluwarsa atau Gagal respon (Bukan 200)
            self.env['sister.sync.log'].create({
                'name': 'Tarik Referensi PT',
                'model_name': 'sister.config',
                'res_id': self.id,
                'status': 'failed',
                'message': f"Status Code: {response.status_code}\nResponse: {response.text[:500]}",
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Akses Ditolak',
                    'message': 'Token mungkin kedaluwarsa (401). Silakan klik Generate Token lagi.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        except Exception as e:
            return self._handle_network_error('Tarik Referensi PT', e)
            
    def _handle_network_error(self, name, e):
        """Format standar log error jaringan"""
        self.env['sister.sync.log'].create({
            'name': name,
            'model_name': 'sister.config',
            'res_id': self.id,
            'status': 'failed',
            'message': str(e),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error Jaringan',
                'message': 'Koneksi ke SISTER gagal, cek koneksi internet / VPN server.',
                'type': 'danger',
                'sticky': False,
            }
        }

    def action_sync_sdm_referensi(self):
        """Menarik Daftar SDM (Dosen) dari SISTER"""
        self.ensure_one()
        url = f"{self.base_url.rstrip('/')}/referensi/sdm"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    HrEmployee = self.env['hr.employee']
                    synced_count = 0
                    
                    for sdm in data:
                        # Respons SISTER umumnya: id_sdm, nama_sdm, status, jenis, dll.
                        id_sdm = sdm.get('id_sdm') or sdm.get('id')
                        nama = sdm.get('nama_sdm') or sdm.get('nama')
                        if id_sdm and nama:
                            employee = HrEmployee.search([('sister_id', '=', id_sdm)], limit=1)
                            if not employee:
                                # Buat data dosen baru, match dengan NIDN akan lebih baik di masa depan jika disediakan.
                                HrEmployee.create({
                                    'name': nama,
                                    'sister_id': id_sdm,
                                })
                            else:
                                employee.write({'name': nama})
                            synced_count += 1
                            
                    self.env['sister.sync.log'].create({
                        'name': 'Sinkronisasi Referensi SDM',
                        'model_name': 'sister.config',
                        'res_id': self.id,
                        'status': 'success',
                        'message': f"Berhasil memproses array SDM. Menarik {synced_count} baris.\nData mentah SISTER: {response.text[:1000]}",
                    })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Sync SDM Berhasil',
                            'message': f'{synced_count} Dosen berhasil ditarik/diperbarui dari SISTER.',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                    
            self.env['sister.sync.log'].create({
                'name': 'Sinkronisasi Referensi SDM',
                'model_name': 'sister.config',
                'res_id': self.id,
                'status': 'failed',
                'message': f"Status Code: {response.status_code}\nResponse: {response.text[:500]}",
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sync Gagal',
                    'message': 'Gagal menarik data SDM dari SISTER. Cek Sync Logs.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        except Exception as e:
            return self._handle_network_error('Sinkronisasi Referensi SDM', e)

class SisterSyncLog(models.Model):
    _name = 'sister.sync.log'
    _description = 'Log Sinkronisasi SISTER'
    _order = 'create_date desc'

    name = fields.Char(string='Aktivitas', required=True)
    model_name = fields.Char(string='Model Odoo')
    res_id = fields.Integer(string='Record ID')
    
    status = fields.Selection([
        ('success', 'Sukses'),
        ('failed', 'Gagal'),
        ('warning', 'Peringatan'),
    ], string='Status', default='success')
    
    message = fields.Text(string='Respon / Pesan API')
    sync_date = fields.Datetime(string='Waktu Sinkron', default=fields.Datetime.now)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sister_id = fields.Char(string='SISTER ID', help='ID Unik Dosen di sistem SISTER Cloud', tracking=True)
    sister_last_sync = fields.Datetime(string='Last SISTER Sync', readonly=True)
    
    pengajaran_ids = fields.One2many('sister.pengajaran', 'employee_id', string='Riwayat Pengajaran', readonly=True)
    publikasi_ids = fields.One2many('sister.publikasi', 'employee_id', string='Riwayat Publikasi', readonly=True)
    pengabdian_ids = fields.One2many('sister.pengabdian', 'employee_id', string='Riwayat Pengabdian', readonly=True)
    
    # Tambahan Kepegawaian
    jafung_ids = fields.One2many('sister.jabatan.fungsional', 'employee_id', string='Jabatan Fungsional', readonly=True)
    kepangkatan_ids = fields.One2many('sister.kepangkatan', 'employee_id', string='Kepangkatan', readonly=True)
    pendidikan_ids = fields.One2many('sister.pendidikan', 'employee_id', string='Pendidikan Formal', readonly=True)
    sertifikasi_ids = fields.One2many('sister.sertifikasi', 'employee_id', string='Sertifikasi', readonly=True)
    
    def action_sync_kepegawaian_to_sister(self):
        """Menarik Jabatan Fungsional, Kepangkatan, Pendidikan, dan Sertifikasi dari SISTER"""
        for record in self:
            if not record.sister_id: continue
            
            config = self.env['sister.config'].search([('is_active', '=', True)], limit=1)
            if not config or not config.api_token: continue
                
            headers = {'Authorization': f'Bearer {config.api_token}', 'Content-Type': 'application/json'}
            msg_log = []
            status_overall = 'success'
            
            endpoints = [
                ('Jabatan Fungsional', f"{config.base_url.rstrip('/')}/jabatan_fungsional?id_sdm={record.sister_id}", 'sister.jabatan.fungsional', 'id_jabatan_fungsional', 'nama_jabatan_fungsional', {'sk_jabatan': 'sk_jabatan'}),
                ('Kepangkatan', f"{config.base_url.rstrip('/')}/kepangkatan?id_sdm={record.sister_id}", 'sister.kepangkatan', 'id_kepangkatan', 'nama_pangkat', {'sk_pangkat': 'sk_pangkat'}),
                ('Pendidikan', f"{config.base_url.rstrip('/')}/pendidikan_formal?id_sdm={record.sister_id}", 'sister.pendidikan', 'id_pendidikan', 'jenjang_pendidikan', {'perguruan_tinggi': 'nama_perguruan_tinggi', 'bidang_studi': 'bidang_studi', 'tahun_lulus': 'tahun_lulus'}),
                ('Sertifikasi', f"{config.base_url.rstrip('/')}/sertifikasi?id_sdm={record.sister_id}", 'sister.sertifikasi', 'id_sertifikasi', 'jenis_sertifikasi', {'bidang_studi': 'bidang_studi', 'nomor_sk': 'nomor_sk', 'tahun_sertifikasi': 'tahun_sertifikasi'}),
            ]
            
            for (title, url, model_name, id_field, name_field, extra_fields) in endpoints:
                try:
                    resp = requests.get(url, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            synced = 0
                            for row in data:
                                raw_id = row.get('id') or row.get(id_field)
                                if not raw_id: continue
                                existing = self.env[model_name].search([(id_field, '=', raw_id)], limit=1)
                                
                                vals = {
                                    'employee_id': record.id,
                                    id_field: raw_id,
                                    'name': row.get(name_field, 'Tidak Diketahui'),
                                }
                                for key_odoo, key_sister in extra_fields.items():
                                    vals[key_odoo] = row.get(key_sister)
                                
                                if existing:
                                    existing.write(vals)
                                else:
                                    self.env[model_name].create(vals)
                                synced += 1
                            msg_log.append(f"{title}: {synced} ditarik.")
                        else:
                            msg_log.append(f"{title}: Kosong.")
                    else:
                        status_overall = 'warning'
                        msg_log.append(f"Gagal {title}: HTTP {resp.status_code}")
                except Exception as e:
                    status_overall = 'warning'
                    msg_log.append(f"Error {title}: {str(e)}")
                    
            record.sister_last_sync = fields.Datetime.now()
            self.env['sister.sync.log'].create({
                'name': f'Sync Kepegawaian Akademik ({record.name})',
                'model_name': 'hr.employee',
                'res_id': record.id,
                'status': status_overall,
                'message': "\n".join(msg_log)
            })
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Proses Tarik Data Kepegawaian & Akademik Selesai!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_sync_publikasi_pengabdian_to_sister(self):
        """Menarik Riwayat Publikasi dan Pengabdian dari SISTER"""
        for record in self:
            if not record.sister_id:
                continue
                
            config = self.env['sister.config'].search([('is_active', '=', True)], limit=1)
            if not config or not config.api_token:
                continue
                
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            # API Publikasi
            url_publikasi = f"{config.base_url.rstrip('/')}/publikasi?id_sdm={record.sister_id}"
            url_pengabdian = f"{config.base_url.rstrip('/')}/pengabdian?id_sdm={record.sister_id}"
            
            msg_log = []
            status_overall = 'success'
            
            # 1. Sync Publikasi
            try:
                resp_pub = requests.get(url_publikasi, headers=headers, timeout=30)
                if resp_pub.status_code == 200:
                    data = resp_pub.json()
                    if isinstance(data, list):
                        synced = 0
                        for row in data:
                            id_pub = row.get('id')
                            if not id_pub: continue
                            existing = self.env['sister.publikasi'].search([('id_publikasi', '=', id_pub)], limit=1)
                            vals = {
                                'employee_id': record.id,
                                'id_publikasi': id_pub,
                                'name': row.get('judul', 'Tanpa Judul'),
                                'kategori_kegiatan': row.get('kategori_kegiatan'),
                                'jenis_publikasi': row.get('jenis_publikasi'),
                                'asal_data': row.get('asal_data'),
                                # "tahun_pelaksanaan" mungkin formatnya tahun, tapi kita butuh Date jika memungkinkan, 
                                # asumsikan kita masukkan 1 Januari dari tahun tersebut jika ada
                                # Atau kita abaikan saja tanggal karena SISTER PublikasiGetItem sering kali tidak mengembalikan tanggal presisi
                            }
                            if existing:
                                existing.write(vals)
                            else:
                                self.env['sister.publikasi'].create(vals)
                            synced += 1
                        msg_log.append(f"Publikasi ditarik: {synced} Data.")
                    else:
                        msg_log.append("Publikasi Kosong.")
                else:
                    msg_log.append(f"Gagal Publikasi: {resp_pub.status_code}")
                    status_overall = 'warning'
            except Exception as e:
                msg_log.append(f"Error Publikasi: {e}")
                status_overall = 'failed'
                
            # 2. Sync Pengabdian
            try:
                resp_peng = requests.get(url_pengabdian, headers=headers, timeout=30)
                if resp_peng.status_code == 200:
                    data = resp_peng.json()
                    if isinstance(data, list):
                        synced = 0
                        for row in data:
                            id_peng = row.get('id')
                            if not id_peng: continue
                            existing = self.env['sister.pengabdian'].search([('id_pengabdian', '=', id_peng)], limit=1)
                            vals = {
                                'employee_id': record.id,
                                'id_pengabdian': id_peng,
                                'name': row.get('judul', 'Tanpa Judul'),
                                'tahun_pelaksanaan': str(row.get('tahun_pelaksanaan', '')),
                                'lama_kegiatan': int(row.get('lama_kegiatan') or 0),
                            }
                            if existing:
                                existing.write(vals)
                            else:
                                self.env['sister.pengabdian'].create(vals)
                            synced += 1
                        msg_log.append(f"Pengabdian ditarik: {synced} Data.")
                    else:
                        msg_log.append("Pengabdian Kosong.")
                else:
                    msg_log.append(f"Gagal Pengabdian: {resp_peng.status_code}")
            except Exception as e:
                msg_log.append(f"Error Pengabdian: {e}")
                
            record.sister_last_sync = fields.Datetime.now()
            
            self.env['sister.sync.log'].create({
                'name': f'Sync Penelitian/Pengabdian ({record.name})',
                'model_name': 'hr.employee',
                'res_id': record.id,
                'status': status_overall,
                'message': "\n".join(msg_log)
            })
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Proses Sinkronisasi Publikasi dan Pengabdian selesai!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_sync_pengajaran_to_sister(self):
        """Menarik Riwayat Pengajaran (Kinerja Dosen) dari SISTER"""
        for record in self:
            if not record.sister_id:
                continue
                
            config = self.env['sister.config'].search([('is_active', '=', True)], limit=1)
            if not config or not config.api_token:
                continue
                
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            # API: /pengajaran
            url_pengajaran = f"{config.base_url.rstrip('/')}/pengajaran?id_sdm={record.sister_id}"
            
            try:
                msg_log = []
                response = requests.get(url_pengajaran, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        synced = 0
                        for row in data:
                            id_pengajaran = row.get('id') or row.get('id_pengajaran')
                            if not id_pengajaran:
                                continue
                                
                            existing = self.env['sister.pengajaran'].search([('id_pengajaran', '=', id_pengajaran)], limit=1)
                            
                            vals = {
                                'employee_id': record.id,
                                'name': row.get('mata_kuliah') or row.get('nama_mata_kuliah') or 'Mata Kuliah Tidak Diketahui',
                                'id_pengajaran': id_pengajaran,
                                'id_semester': row.get('id_semester'),  # Bisa jadi None
                                'nama_semester': row.get('semester') or row.get('nama_semester'),
                                'kode_mata_kuliah': row.get('kode_mata_kuliah'),
                                'nama_kelas_kuliah': row.get('kelas') or row.get('nama_kelas_kuliah'),
                                'sks': float(row.get('sks_mata_kuliah') or row.get('sks') or 0),
                                'jumlah_mahasiswa_krs': int(row.get('jumlah_mahasiswa') or 0),
                            }
                            
                            if existing:
                                existing.write(vals)
                            else:
                                self.env['sister.pengajaran'].create(vals)
                            synced += 1
                            
                        msg_log.append(f"Riwayat Pengajaran berhasil ditarik. {synced} Kelas ditemukan.")
                    else:
                        msg_log.append("Respons SISTER bukan array (Kosong).")
                else:
                    msg_log.append(f"Gagal tarik pengajaran. Status: {response.status_code}")

                record.sister_last_sync = fields.Datetime.now()
                
                self.env['sister.sync.log'].create({
                    'name': f'Sync Pengajaran ({record.name})',
                    'model_name': 'hr.employee',
                    'res_id': record.id,
                    'status': 'success' if response.status_code == 200 else 'warning',
                    'message': "\n".join(msg_log) + f"\nResponse Mentah: {response.text[:1000]}",
                })
                
            except Exception as e:
                self.env['sister.sync.log'].create({
                    'name': f'Sync Pengajaran ({record.name})',
                    'model_name': 'hr.employee',
                    'res_id': record.id,
                    'status': 'failed',
                    'message': str(e),
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Proses penarikan Pengajaran (Kinerja Dosen) selesai, silakan cek log!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_sync_to_sister(self):
        """Menarik Detail Profil Pribadi & Kepegawaian dari SISTER"""
        for record in self:
            if not record.sister_id:
                continue
                
            config = self.env['sister.config'].search([('is_active', '=', True)], limit=1)
            if not config or not config.api_token:
                continue # Atau raise ValidationError jika dipicu by button
                
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json'
            }
            
            # API: Tarik profil detail
            url_profil = f"{config.base_url.rstrip('/')}/data_pribadi/profil/{record.sister_id}"
            
            try:
                msg_log = []
                response = requests.get(url_profil, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Pemetaan dari kembalian profil (contoh struktur mapping JSON yang umum/antisipatif)
                    nidn = data.get('nidn') or data.get('nidin')
                    jk = data.get('jenis_kelamin')
                    
                    update_vals = {}
                    if nidn:
                        update_vals['identification_id'] = nidn
                    if jk == 'L':
                        update_vals['gender'] = 'male'
                    elif jk == 'P':
                        update_vals['gender'] = 'female'
                        
                    if update_vals:
                        record.write(update_vals)
                        
                    msg_log.append("Profil berhasil diperbarui dari SISTER (NIDN/Gender dll).")
                else:
                    msg_log.append(f"Gagal tarik profil. Status: {response.status_code}")

                record.sister_last_sync = fields.Datetime.now()
                
                self.env['sister.sync.log'].create({
                    'name': f'Sync Profil SDM ({record.name})',
                    'model_name': 'hr.employee',
                    'res_id': record.id,
                    'status': 'success' if response.status_code == 200 else 'warning',
                    'message': "\n".join(msg_log) + f"\nResponse Terakhir: {response.text[:200]}",
                })
                
            except Exception as e:
                self.env['sister.sync.log'].create({
                    'name': f'Sync Profil SDM ({record.name})',
                    'model_name': 'hr.employee',
                    'res_id': record.id,
                    'status': 'failed',
                    'message': str(e),
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Proses penarikan Profil SISTER selesai, silakan cek log untuk mendetail!',
                'type': 'success',
                'sticky': False,
            }
        }

class SimMataKuliah(models.Model):
    _inherit = 'sim.akademik.mata.kuliah'

    sister_id = fields.Char(string='SISTER ID (Matkul)', help='Pemetaan Kode Matkul di SISTER', tracking=True)
