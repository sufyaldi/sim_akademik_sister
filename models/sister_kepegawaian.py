# -*- coding: utf-8 -*-
from odoo import models, fields

class SisterJabatanFungsional(models.Model):
    _name = 'sister.jabatan.fungsional'
    _description = 'Riwayat Jabatan Fungsional Dosen (SISTER)'
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    sister_id = fields.Char(related='employee_id.sister_id', store=True)
    
    id_jabatan_fungsional = fields.Char(string='ID Jafung', required=True)
    name = fields.Char(string='Jabatan Fungsional', required=True) # e.g., "Lektor Kepala"
    sk_jabatan = fields.Char(string='SK Jabatan')

    _sql_constraints = [('unique_id_jafung', 'unique(id_jabatan_fungsional)', 'ID Jafung SISTER harus unik!')]

class SisterKepangkatan(models.Model):
    _name = 'sister.kepangkatan'
    _description = 'Riwayat Kepangkatan Dosen (SISTER)'
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    
    id_kepangkatan = fields.Char(string='ID Kepangkatan', required=True)
    name = fields.Char(string='Pangkat / Golongan', required=True) # e.g., "Penata / III/c"
    sk_pangkat = fields.Char(string='SK Pangkat')

    _sql_constraints = [('unique_id_kepangkatan', 'unique(id_kepangkatan)', 'ID Kepangkatan SISTER harus unik!')]

class SisterPendidikan(models.Model):
    _name = 'sister.pendidikan'
    _description = 'Riwayat Pendidikan Formal Dosen (SISTER)'
    _order = 'tahun_lulus desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    id_pendidikan = fields.Char(string='ID Pendidikan', required=True)
    name = fields.Char(string='Jenjang', required=True)
    perguruan_tinggi = fields.Char(string='Perguruan Tinggi / Sekolah')
    bidang_studi = fields.Char(string='Bidang Studi / Gelar')
    tahun_lulus = fields.Char(string='Tahun Lulus')

    _sql_constraints = [('unique_id_pendidikan', 'unique(id_pendidikan)', 'ID Pendidikan SISTER harus unik!')]

class SisterSertifikasi(models.Model):
    _name = 'sister.sertifikasi'
    _description = 'Sertifikasi Dosen (SISTER)'
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    id_sertifikasi = fields.Char(string='ID Sertifikasi', required=True)
    name = fields.Char(string='Jenis Sertifikasi', required=True)
    bidang_studi = fields.Char(string='Bidang Studi')
    nomor_sk = fields.Char(string='Nomor SK')
    tahun_sertifikasi = fields.Char(string='Tahun')

    _sql_constraints = [('unique_id_sertifikasi', 'unique(id_sertifikasi)', 'ID Sertifikasi SISTER harus unik!')]
