from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    MasterDepartemen, MasterJabatan, MasterCabang, MasterMesin,
    Pegawai, Absensi, FingerprintTemplate,
    MasterModeJamKerja, ModeJamKerjaJadwal, ModeJamKerjaPeriode,
    TapLog, AbsensiSesi, TapSesiRelation,
    PegawaiModeAssignment  
)

# ==============================================================================
# ADMIN - MODE JAM KERJA
# ==============================================================================

@admin.register(MasterModeJamKerja)
class MasterModeJamKerjaAdmin(admin.ModelAdmin):
    """Admin untuk mode jam kerja"""
    
    list_display = [
        'nama', 
        'kode', 
        'warna_display',
        'priority', 
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'priority',
        'is_active',
        'created_at'
    ]
    
    search_fields = ['nama', 'kode']
    ordering = ['-priority', 'nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama', 'kode', 'warna', 'priority')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warna_display(self, obj):
        """Display preview warna"""
        return format_html(
            '<div style="width:30px;height:30px;background:{};border-radius:5px;border:1px solid #ccc;"></div>',
            obj.warna
        )
    
    warna_display.short_description = 'Warna'


@admin.register(ModeJamKerjaJadwal)
class ModeJamKerjaJadwalAdmin(admin.ModelAdmin):
    """Admin untuk jadwal mode jam kerja"""
    
    list_display = [
        'mode',
        'group_name',
        'hari_display',
        'jam_kerja_display',
        'urutan'
    ]
    
    list_filter = [
        'mode',
        'group_name',
        'hari'
    ]
    
    search_fields = [
        'mode__nama',
        'group_name'
    ]
    
    ordering = ['mode', 'group_name', 'hari', 'urutan']
    
    fieldsets = (
        ('Relasi', {
            'fields': ('mode', 'group_name')
        }),
        ('Hari & Urutan', {
            'fields': ('hari', 'urutan')
        }),
        ('Jam Kerja', {
            'fields': (
                'jam_masuk',
                'jam_keluar',
                'jam_istirahat_keluar',
                'jam_istirahat_masuk'
            )
        }),
        ('Toleransi', {
            'fields': (
                'toleransi_terlambat',
                'toleransi_pulang_cepat'
            )
        }),
    )
    
    def hari_display(self, obj):
        """Tampilkan nama hari"""
        hari_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        return hari_names[obj.hari]
    
    hari_display.short_description = 'Hari'
    
    def jam_kerja_display(self, obj):
        """Tampilkan jam kerja dalam format readable"""
        return obj.get_jam_kerja_display()
    
    jam_kerja_display.short_description = 'Jam Kerja'


# Form untuk Periode dengan Color Picker
class ModeJamKerjaPeriodeForm(forms.ModelForm):
    warna_periode = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'color',
            'style': 'width: 100px; height: 40px; cursor: pointer;'
        }),
        required=False,
        help_text='Pilih warna untuk periode khusus (libur nasional, ramadhan, dll)'
    )
    
    class Meta:
        model = ModeJamKerjaPeriode
        fields = '__all__'


@admin.register(ModeJamKerjaPeriode)
class ModeJamKerjaPeriodeAdmin(admin.ModelAdmin):
    """Admin untuk periode mode jam kerja dengan color picker"""
    
    form = ModeJamKerjaPeriodeForm
    
    list_display = [
        'nama',
        'mode',
        'tanggal_mulai',
        'tanggal_selesai',
        'tahun',
        'is_periode_khusus',
        'warna_preview',
        'is_active'
    ]
    
    list_filter = [
        'mode',
        'tahun',
        'is_periode_khusus',
        'is_active'
    ]
    
    search_fields = ['nama', 'mode__nama']
    ordering = ['-tanggal_mulai']
    
    fieldsets = (
        ('Informasi Periode', {
            'fields': ('mode', 'nama', 'catatan')
        }),
        ('Tanggal', {
            'fields': (
                'tanggal_mulai',
                'tanggal_selesai',
                'tahun'
            )
        }),
        ('Periode Khusus', {
            'fields': ('is_periode_khusus', 'warna_periode'),
            'description': 'Centang "Periode Khusus" untuk periode seperti libur nasional, ramadhan, dll. Pilih warna yang akan ditampilkan di riwayat absensi.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def warna_preview(self, obj):
        """Display preview warna periode"""
        if obj.warna_periode:
            return format_html(
                '<div style="width: 40px; height: 30px; background: {}; border: 2px solid #ccc; border-radius: 6px;"></div>',
                obj.warna_periode
            )
        return format_html('<span style="color: #9ca3af;">-</span>')
    
    warna_preview.short_description = 'Warna'


# ==============================================================================
# ADMIN - MASTER DATA ORGANISASI
# ==============================================================================

@admin.register(MasterDepartemen)
class MasterDepartemenAdmin(admin.ModelAdmin):
    """Admin untuk master departemen"""
    
    list_display = ['id_departemen', 'nama', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['nama', 'id_departemen']
    ordering = ['id_departemen', 'nama']


@admin.register(MasterJabatan)
class MasterJabatanAdmin(admin.ModelAdmin):
    """Admin untuk master jabatan"""
    
    list_display = ['kode', 'nama', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['nama', 'kode']
    ordering = ['nama']


@admin.register(MasterCabang)
class MasterCabangAdmin(admin.ModelAdmin):
    """Admin untuk master cabang"""
    
    list_display = ['kode', 'nama', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['nama', 'kode', 'alamat']
    ordering = ['nama']


@admin.register(MasterMesin)
class MasterMesinAdmin(admin.ModelAdmin):
    """Admin untuk master mesin absensi"""
    
    list_display = ['kode', 'nama', 'ip_address', 'port', 'cabang', 'is_active']
    list_filter = ['is_active', 'cabang']
    search_fields = ['nama', 'kode', 'ip_address']
    ordering = ['cabang', 'nama']


# ==============================================================================
# ADMIN - DATA PEGAWAI
# ==============================================================================

@admin.register(Pegawai)
class PegawaiAdmin(admin.ModelAdmin):
    """Admin untuk data pegawai"""
    
    list_display = [
        'userid',
        'nama_lengkap',
        'departemen',
        'jabatan',
        'cabang',
        'mode_jam_kerja',
        'is_active'
    ]
    
    list_filter = [
        'is_active',
        'departemen',
        'jabatan',
        'cabang',
        'mode_jam_kerja',
        'is_shift_worker'
    ]
    
    search_fields = [
        'userid',
        'nama_lengkap',
        'email',
        'nomor_hp'
    ]
    
    ordering = ['userid']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FingerprintTemplate)
class FingerprintTemplateAdmin(admin.ModelAdmin):
    """Admin untuk template fingerprint"""
    
    list_display = [
        'pegawai',
        'uid',
        'fid',
        'size',
        'valid',
        'created_at'
    ]
    
    list_filter = ['valid', 'created_at']
    
    search_fields = [
        'pegawai__nama_lengkap',
        'pegawai__userid'
    ]
    
    ordering = ['pegawai', 'fid']


# ==============================================================================
# ADMIN - DATA ABSENSI
# ==============================================================================

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    """Admin untuk data absensi"""
    
    list_display = [
        'pegawai',
        'tanggal',
        'tap_masuk',
        'tap_pulang',
        'status',
        'is_late',
        'is_early_departure'
    ]
    
    list_filter = [
        'status',
        'is_late',
        'is_early_departure',
        'tanggal'
    ]
    
    search_fields = [
        'pegawai__nama_lengkap',
        'pegawai__userid'
    ]
    
    ordering = ['-tanggal', 'pegawai__userid']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TapLog)
class TapLogAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'tanggal', 'waktu_tap', 'punch_type', 'is_processed']
    list_filter = ['tanggal', 'punch_type', 'is_processed']
    search_fields = ['pegawai__nama_lengkap', 'pegawai__userid']
    date_hierarchy = 'tanggal'

@admin.register(AbsensiSesi)
class AbsensiSesiAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'tanggal_mulai', 'tap_masuk_pertama', 'tap_pulang_terakhir', 'status', 'durasi_kerja_menit']
    list_filter = ['status', 'is_cross_day', 'tanggal_mulai']
    search_fields = ['pegawai__nama_lengkap', 'pegawai__userid']
    date_hierarchy = 'tanggal_mulai'

@admin.register(TapSesiRelation)
class TapSesiRelationAdmin(admin.ModelAdmin):
    list_display = ['tap_log', 'absensi_sesi', 'urutan_dalam_sesi']
    list_filter = ['absensi_sesi__tanggal_mulai']