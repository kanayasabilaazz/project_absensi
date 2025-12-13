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
        'cabang',
        'is_default',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'priority',
        'is_default',
        'is_active',
        'cabang',
        'created_at'
    ]
    
    search_fields = ['nama', 'kode']
    ordering = ['-priority', 'nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama', 'kode', 'warna', 'icon', 'priority')
        }),
        ('Scope & Status', {
            'fields': ('cabang', 'is_default', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warna_display(self, obj):
        """Display preview warna"""
        return format_html(
            '<div style="width:30px;height:30px;background:{};'
            'border-radius:5px;border:1px solid #ccc;"></div>',
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
        if obj.jam_masuk and obj.jam_keluar:
            return f"{obj.jam_masuk.strftime('%H:%M')} - {obj.jam_keluar.strftime('%H:%M')}"
        return "-"
    
    jam_kerja_display.short_description = 'Jam Kerja'


class ModeJamKerjaPeriodeForm(forms.ModelForm):
    """Custom form dengan color picker untuk periode"""
    
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
    readonly_fields = ['created_at']
    
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
            'description': 'Centang "Periode Khusus" untuk periode seperti libur nasional, '
                          'ramadhan, dll. Pilih warna yang akan ditampilkan di riwayat absensi.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def warna_preview(self, obj):
        """Display preview warna periode"""
        if obj.warna_periode:
            return format_html(
                '<div style="width: 40px; height: 30px; background: {}; '
                'border: 2px solid #ccc; border-radius: 6px;"></div>',
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
    list_filter = ['is_active', 'created_at']
    search_fields = ['nama', 'id_departemen', 'keterangan']
    ordering = ['id_departemen', 'nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Departemen', {
            'fields': ('id_departemen', 'nama', 'keterangan')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MasterJabatan)
class MasterJabatanAdmin(admin.ModelAdmin):
    """Admin untuk master jabatan"""
    
    list_display = ['kode', 'nama', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nama', 'kode', 'keterangan']
    ordering = ['nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Jabatan', {
            'fields': ('kode', 'nama', 'keterangan')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MasterCabang)
class MasterCabangAdmin(admin.ModelAdmin):
    """Admin untuk master cabang"""
    
    list_display = ['kode', 'nama', 'port_mesin', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nama', 'kode', 'alamat']
    ordering = ['nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Cabang', {
            'fields': ('kode', 'nama', 'alamat')
        }),
        ('Mesin Fingerprint', {
            'fields': ('ip_mesin_fingerprint', 'port_mesin')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MasterMesin)
class MasterMesinAdmin(admin.ModelAdmin):
    """Admin untuk master mesin absensi"""
    
    list_display = ['kode', 'nama', 'ip_address', 'port', 'cabang', 'is_active']
    list_filter = ['is_active', 'cabang', 'created_at']
    search_fields = ['nama', 'kode', 'ip_address', 'lokasi']
    ordering = ['cabang', 'nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Mesin', {
            'fields': ('kode', 'nama', 'cabang')
        }),
        ('Koneksi', {
            'fields': ('ip_address', 'port')
        }),
        ('Detail', {
            'fields': ('lokasi', 'keterangan')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
        'is_shift_worker',
        'is_active'
    ]
    
    list_filter = [
        'is_active',
        'is_shift_worker',
        'departemen',
        'jabatan',
        'cabang',
        'mode_jam_kerja'
    ]
    
    search_fields = [
        'userid',
        'nama_lengkap',
        'email',
        'nomor_hp'
    ]
    
    ordering = ['userid']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identitas', {
            'fields': ('userid', 'nama_lengkap', 'email', 'nomor_hp', 'alamat', 'tanggal_lahir')
        }),
        ('Organisasi', {
            'fields': ('departemen', 'jabatan', 'cabang')
        }),
        ('Jam Kerja', {
            'fields': ('mode_jam_kerja', 'is_shift_worker')
        }),
        ('Mesin Absensi', {
            'fields': ('mesin', 'uid_mesin')
        }),
        ('Status & Tanggal', {
            'fields': ('tanggal_bergabung', 'tanggal_nonaktif', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
    readonly_fields = ['created_at']


@admin.register(PegawaiModeAssignment)
class PegawaiModeAssignmentAdmin(admin.ModelAdmin):
    """Admin untuk assignment pegawai ke mode jam kerja"""
    
    list_display = [
        'pegawai',
        'mode',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'mode',
        'created_at'
    ]
    
    search_fields = [
        'pegawai__nama_lengkap',
        'pegawai__userid',
        'mode__nama'
    ]
    
    ordering = ['pegawai', 'mode']
    readonly_fields = ['created_at', 'updated_at']


# ==============================================================================
# ADMIN - DATA ABSENSI
# ==============================================================================

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    """Admin untuk data absensi (Legacy)"""
    
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
    
    date_hierarchy = 'tanggal'
    ordering = ['-tanggal', 'pegawai__userid']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TapLog)
class TapLogAdmin(admin.ModelAdmin):
    """Admin untuk tap log"""
    
    list_display = [
        'pegawai',
        'tanggal',
        'waktu_tap',
        'punch_type',
        'mesin',
        'is_processed'
    ]
    
    list_filter = [
        'tanggal',
        'punch_type',
        'is_processed',
        'mesin'
    ]
    
    search_fields = [
        'pegawai__nama_lengkap',
        'pegawai__userid'
    ]
    
    date_hierarchy = 'tanggal'
    ordering = ['-tanggal', '-waktu_tap']
    readonly_fields = ['created_at']


@admin.register(AbsensiSesi)
class AbsensiSesiAdmin(admin.ModelAdmin):
    """Admin untuk sesi absensi"""
    
    list_display = [
        'pegawai',
        'tanggal_mulai',
        'tap_masuk_pertama',
        'tap_pulang_terakhir',
        'status',
        'is_cross_day',
        'durasi_kerja_menit'
    ]
    
    list_filter = [
        'status',
        'is_cross_day',
        'tanggal_mulai'
    ]
    
    search_fields = [
        'pegawai__nama_lengkap',
        'pegawai__userid'
    ]
    
    date_hierarchy = 'tanggal_mulai'
    ordering = ['-tanggal_mulai', 'pegawai']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TapSesiRelation)
class TapSesiRelationAdmin(admin.ModelAdmin):
    """Admin untuk relasi tap log dan sesi"""
    
    list_display = [
        'tap_log',
        'absensi_sesi',
        'urutan_dalam_sesi',
        'created_at'
    ]
    
    list_filter = [
        'absensi_sesi__tanggal_mulai',
        'created_at'
    ]
    
    ordering = ['absensi_sesi', 'urutan_dalam_sesi']
    readonly_fields = ['created_at']