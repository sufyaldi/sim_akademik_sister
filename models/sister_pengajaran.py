# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SisterPengajaran(models.Model):
    _name = 'sister.pengajaran'
    _description = 'Riwayat Pengajaran SISTER (Kinerja Dosen)'
    _order = 'id_semester desc, name asc'

    name = fields.Char(string='Mata Kuliah', required=True)
    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    sister_id = fields.Char(string='ID Pegawai SISTER', related='employee_id.sister_id', store=True)
    
    id_pengajaran = fields.Char(string='ID Pengajaran SISTER', help='UUID Unik Pengajaran dari SISTER', required=True)
    
    id_semester = fields.Char(string='Semester (ID)')
    nama_semester = fields.Char(string='Semester')
    
    kode_mata_kuliah = fields.Char(string='Kode Matkul')
    nama_kelas_kuliah = fields.Char(string='Kelas')
    
    sks = fields.Float(string='SKS', help='SKS Mata Kuliah')
    sks_tatap_muka = fields.Float(string='SKS Tatap Muka')
    sks_praktek = fields.Float(string='SKS Praktikum')
    
    jumlah_mahasiswa_krs = fields.Integer(string='Jml Mhs KRS')
    
    # Menghubungkan ke tabel sim.akademik.mata.kuliah jika diperlukan integrasi 2 arah
    mata_kuliah_id = fields.Many2one('sim.akademik.mata.kuliah', string='Matkul Internal')

    _sql_constraints = [
        ('unique_id_pengajaran', 'unique(id_pengajaran)', 'ID Pengajaran SISTER harus unik!')
    ]
