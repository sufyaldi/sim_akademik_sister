# -*- coding: utf-8 -*-

from odoo import models, fields

class SisterPublikasi(models.Model):
    _name = 'sister.publikasi'
    _description = 'Riwayat Publikasi SISTER (Kinerja Dosen)'
    _order = 'tanggal desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    sister_id = fields.Char(string='ID Pegawai SISTER', related='employee_id.sister_id', store=True)
    
    id_publikasi = fields.Char(string='ID Publikasi', required=True)
    name = fields.Char(string='Judul Publikasi', required=True)
    kategori_kegiatan = fields.Char(string='Kategori Kegiatan')
    jenis_publikasi = fields.Char(string='Jenis Publikasi')
    tanggal = fields.Date(string='Tanggal Terbit')
    asal_data = fields.Char(string='Sumber Data')

    _sql_constraints = [
        ('unique_id_publikasi', 'unique(id_publikasi)', 'ID Publikasi SISTER harus unik!')
    ]

class SisterPengabdian(models.Model):
    _name = 'sister.pengabdian'
    _description = 'Riwayat Pengabdian SISTER (Kinerja Dosen)'
    _order = 'tahun_pelaksanaan desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Dosen', ondelete='cascade', required=True)
    sister_id = fields.Char(string='ID Pegawai SISTER', related='employee_id.sister_id', store=True)

    id_pengabdian = fields.Char(string='ID Pengabdian', required=True)
    name = fields.Char(string='Judul Pengabdian', required=True)
    tahun_pelaksanaan = fields.Char(string='Tahun Pelaksanaan')
    lama_kegiatan = fields.Integer(string='Lama Kegiatan (Tahun)')

    _sql_constraints = [
        ('unique_id_pengabdian', 'unique(id_pengabdian)', 'ID Pengabdian SISTER harus unik!')
    ]
