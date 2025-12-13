"""
URL Configuration - Project Absensi
Routing untuk sistem absensi dengan integrasi fingerprint
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # AUTH
    # ============================================================
    path('', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # ============================================================
    # DASHBOARD
    # ============================================================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/detail-absensi/', views.detail_absensi_by_status, name='detail_absensi_by_status'),
    path('dashboard/riwayat-hari-ini/', views.riwayat_absensi_hari_ini, name='riwayat_absensi_hari_ini'),
    path('dashboard/statistik/', views.statistik_absensi, name='statistik_absensi'),

    # ============================================================
    # PEGAWAI - CRUD & DETAIL
    # ============================================================
    path('pegawai/', views.daftar_Pegawai, name='daftar_Pegawai'),
    path('pegawai/<int:pk>/', views.Pegawai_detail, name='Pegawai_detail'),
    path('pegawai/<int:pk>/edit/', views.Pegawai_edit, name='Pegawai_edit'),
    path('pegawai/<int:pk>/hapus/', views.Pegawai_hapus, name='Pegawai_hapus'),
    path('pegawai/<int:pk>/toggle-status/', views.toggle_pegawai_status, name='toggle_pegawai_status'),
    path('pegawai/<int:pk>/riwayat/', views.riwayat_absensi_per_pegawai, name='riwayat_per_Pegawai'),

    # ============================================================
    # PEGAWAI - REGISTRASI
    # ============================================================
    path('pegawai/register/menu/', views.register_Pegawai_menu, name='register_Pegawai_menu'),
    path('pegawai/register/manual/', views.register_Pegawai, name='register_Pegawai_manual'),
    path('pegawai/register/dari-mesin/', views.register_Pegawai_dari_mesin, name='register_Pegawai_dari_mesin'),
    path('pegawai/register/dari-mesin/ambil/', views.ambil_user_dari_mesin, name='ambil_user_dari_mesin'),
    path('pegawai/register/dari-mesin/simpan/', views.simpan_Pegawai_dari_mesin, name='simpan_Pegawai_dari_mesin'),

    # ============================================================
    # PEGAWAI - SINKRONISASI MESIN
    # ============================================================
    path('pegawai/sync/ke-mesin/', views.register_Pegawai_ke_mesin, name='sinkron_ke_mesin'),
    path('pegawai/sync/daftar-ke-mesin/', views.daftarkan_Pegawai_ke_mesin, name='daftarkan_Pegawai_ke_mesin'),
    path('pegawai/sync/uid/', views.sync_semua_uid_dari_mesin, name='sync_semua_uid'),
    path('pegawai/sync/fingerprint/', views.sync_fingerprint_from_machine, name='sync_fingerprint_from_machine'),

    # ============================================================
    # PEGAWAI - TRANSFER ANTAR MESIN
    # ============================================================
    path('pegawai/transfer/menu/', views.transfer_pegawai_ke_mesin, name='transfer_pegawai_ke_mesin'),
    path('pegawai/transfer/proses/', views.proses_transfer_pegawai, name='proses_transfer_pegawai'),
    path('pegawai/transfer/bulk/', views.bulk_transfer_pegawai, name='bulk_transfer_pegawai'),

    # ============================================================
    # PEGAWAI - MODE JAM KERJA
    # ============================================================
    path('pegawai/assign-mode-jam-kerja/<int:pegawai_id>/', views.assign_mode_jam_kerja_pegawai, name='assign_mode_jam_kerja_pegawai'),
    path('pegawai/<int:pegawai_id>/simpan-assign-mode/', views.simpan_assign_mode_jam_kerja, name='simpan_assign_mode_jam_kerja'),
    path('pegawai/daftar-assign-mode/', views.daftar_assign_mode_pegawai, name='daftar_assign_mode_pegawai'),

    # ============================================================
    # PEGAWAI - BULK ACTIONS
    # ============================================================
    path('pegawai/bulk/activate/', views.bulk_activate_pegawai, name='bulk_activate_pegawai'),
    path('pegawai/bulk/deactivate/', views.bulk_deactivate_pegawai, name='bulk_deactivate_pegawai'),
    path('pegawai/bulk/delete/', views.bulk_delete_pegawai, name='bulk_delete_pegawai'),

    # ============================================================
    # ABSENSI
    # ============================================================
    path('absensi/', views.riwayat_absensi, name='riwayat_absensi'),
    path('absensi/catat/', views.absensi_admin, name='absensi_admin'),
    path('absensi/<int:pk>/edit/', views.absensi_edit, name='absensi_edit'),
    path('absensi/<int:pk>/hapus/', views.absensi_hapus, name='absensi_hapus'),
    path('absensi/sync/', views.sync_absensi, name='sync_absensi'),

    # ============================================================
    # TAP LOG & SESI ABSENSI
    # ============================================================
    path('tap/sync-to-log/', views.sync_tap_to_log, name='sync_tap_to_log'),
    path('tap/proses-to-sesi/', views.proses_tap_to_sesi, name='proses_tap_to_sesi'),
    path('sesi/riwayat/', views.riwayat_sesi_absensi, name='riwayat_sesi_absensi'),
    path('sesi/pegawai/<int:pk>/', views.riwayat_sesi_per_pegawai, name='riwayat_sesi_per_pegawai'),
    path('sesi/<int:pk>/hapus/', views.hapus_sesi_absensi, name='hapus_sesi_absensi'),

    # ============================================================
    # MONITORING MESIN
    # ============================================================
    path('monitor/mesin/', views.monitor_absensi_mesin, name='monitor_absensi_mesin'),
    path('monitor/mesin/status/', views.check_all_machines_status, name='check_all_machines_status'),
    path('monitor/mesin/cek-bulk/', views.cek_status_mesin_bulk, name='cek_status_mesin_bulk'),

    # ============================================================
    # EKSPOR LAPORAN
    # ============================================================
    path('export/menu/', views.export_menu, name='export_menu'),
    path('export/csv/', views.export_absensi_csv_advanced, name='export_absensi_csv_advanced'),
    path('export/preview/', views.preview_export_data, name='preview_export_data'),
    path('export/statistik/', views.export_statistik_absensi, name='export_statistik_absensi'),

    # ============================================================
    # PENGATURAN - MENU UTAMA
    # ============================================================
    path('pengaturan/', views.menu_pengaturan, name='menu_pengaturan'),

    # ============================================================
    # PENGATURAN - DEPARTEMEN
    # ============================================================
    path('pengaturan/departemen/', views.daftar_departemen, name='daftar_departemen'),
    path('pengaturan/departemen/tambah/', views.tambah_departemen, name='tambah_departemen'),
    path('pengaturan/departemen/<int:pk>/edit/', views.edit_departemen, name='edit_departemen'),
    path('pengaturan/departemen/<int:pk>/hapus/', views.hapus_departemen, name='hapus_departemen'),

    # ============================================================
    # PENGATURAN - JABATAN
    # ============================================================
    path('pengaturan/jabatan/', views.daftar_jabatan, name='daftar_jabatan'),
    path('pengaturan/jabatan/tambah/', views.tambah_jabatan, name='tambah_jabatan'),
    path('pengaturan/jabatan/<int:pk>/edit/', views.edit_jabatan, name='edit_jabatan'),
    path('pengaturan/jabatan/<int:pk>/hapus/', views.hapus_jabatan, name='hapus_jabatan'),

    # ============================================================
    # PENGATURAN - CABANG
    # ============================================================
    path('pengaturan/cabang/', views.daftar_cabang, name='daftar_cabang'),
    path('pengaturan/cabang/tambah/', views.tambah_cabang, name='tambah_cabang'),
    path('pengaturan/cabang/<int:pk>/edit/', views.edit_cabang, name='edit_cabang'),
    path('pengaturan/cabang/<int:pk>/hapus/', views.hapus_cabang, name='hapus_cabang'),

    # ============================================================
    # PENGATURAN - MESIN FINGERPRINT
    # ============================================================
    path('pengaturan/mesin/', views.daftar_mesin, name='daftar_mesin'),
    path('pengaturan/mesin/tambah/', views.tambah_mesin, name='tambah_mesin'),
    path('pengaturan/mesin/<int:pk>/edit/', views.edit_mesin, name='edit_mesin'),
    path('pengaturan/mesin/<int:pk>/hapus/', views.hapus_mesin, name='hapus_mesin'),
    path('pengaturan/mesin/<int:pk>/test/', views.test_mesin, name='test_mesin'),

    # ============================================================
    # PENGATURAN - ADMIN
    # ============================================================
    path('pengaturan/admin/', views.daftar_admin, name='daftar_admin'),
    path('pengaturan/admin/tambah/', views.tambah_admin, name='tambah_admin'),
    path('pengaturan/admin/<int:pk>/edit/', views.edit_admin, name='edit_admin'),
    path('pengaturan/admin/<int:pk>/reset-password/', views.reset_password_admin, name='reset_password_admin'),
    path('pengaturan/admin/<int:pk>/hapus/', views.hapus_admin, name='hapus_admin'),

    # ============================================================
    # PENGATURAN - MODE JAM KERJA
    # ============================================================
    path('pengaturan/mode-jam-kerja/', views.daftar_mode_jam_kerja, name='daftar_mode_jam_kerja'),
    path('pengaturan/mode-jam-kerja/tambah/', views.tambah_mode_jam_kerja, name='tambah_mode_jam_kerja'),
    path('pengaturan/mode-jam-kerja/<int:pk>/', views.detail_mode_jam_kerja, name='detail_mode_jam_kerja'),
    path('pengaturan/mode-jam-kerja/<int:pk>/edit/', views.edit_mode_jam_kerja, name='edit_mode_jam_kerja'),
    path('pengaturan/mode-jam-kerja/<int:pk>/hapus/', views.hapus_mode_jam_kerja, name='hapus_mode_jam_kerja'),
    path('pengaturan/mode-jam-kerja/<int:pk>/duplicate/', views.duplicate_mode_jam_kerja, name='duplicate_mode_jam_kerja'),

    # ============================================================
    # PENGATURAN - PERIODE MODE JAM KERJA
    # ============================================================
    path('pengaturan/mode-jam-kerja/<int:mode_id>/periode/', views.daftar_periode_mode, name='daftar_periode_mode'),
    path('pengaturan/mode-jam-kerja/<int:mode_id>/periode/tambah/', views.tambah_periode_mode, name='tambah_periode_mode'),
    path('pengaturan/periode/<int:pk>/edit/', views.edit_periode_mode, name='edit_periode_mode'),
    path('pengaturan/periode/<int:pk>/hapus/', views.hapus_periode_mode, name='hapus_periode_mode'),

    # ============================================================
    # API - DASHBOARD
    # ============================================================
    path('api/pegawai/status-summary/', views.get_pegawai_status_summary, name='get_pegawai_status_summary'),
    path('api/mode-today/', views.api_get_mode_today, name='api_get_mode_today'),

    # ============================================================
    # API - PEGAWAI
    # ============================================================
    path('api/pegawai/cek-userid/', views.cek_userid_tersedia, name='cek_userid_tersedia'),
    path('api/pegawai/generate-userid/', views.generate_userid_otomatis, name='generate_userid_otomatis'),
    path('api/pegawai/by-cabang/', views.get_pegawai_by_cabang, name='get_pegawai_by_cabang'),
    path('api/pegawai/cek-di-mesin/', views.cek_pegawai_di_mesin, name='cek_pegawai_di_mesin'),
    path('api/pegawai/get-modes/', views.api_get_applicable_modes, name='api_get_applicable_modes'),
    path('api/pegawai/get-mesin-by-pegawai/', views.api_get_mesin_by_pegawai, name='api_get_mesin_by_pegawai'),
    path('api/pegawai/<int:pegawai_id>/mode-assignments/', views.api_get_mode_assignments, name='api_get_mode_assignments'),
    path('pegawai/api/get-mesin-by-pegawai/', views.api_get_mesin_by_pegawai, name='api_get_mesin_by_pegawai'),

    # ============================================================
    # API - ABSENSI
    # ============================================================
    path('api/absensi/dari-mesin/', views.get_absensi_dari_mesin, name='api_get_absensi_dari_mesin'),
    path('api/absensi/all-machines/', views.get_absensi_all_machines, name='api_get_absensi_all_machines'),

    # ============================================================
    # API - TAP LOG & SESI
    # ============================================================
    path('api/tap-logs/<int:pegawai_id>/', views.api_get_tap_logs, name='api_get_tap_logs'),
    path('api/sesi/<int:sesi_id>/', views.api_get_sesi_detail, name='api_get_sesi_detail'),
    path('api/sesi/statistics/', views.api_get_sesi_statistics, name='api_get_sesi_statistics'),
    path('api/sesi/<int:pk>/hapus/', views.api_hapus_sesi, name='api_hapus_sesi'),

    # ============================================================
    # API - CABANG
    # ============================================================
    path('api/switch-cabang/', views.switch_cabang, name='switch_cabang'),
    path('api/cabang/aktif/', views.get_cabang_aktif, name='get_cabang_aktif'),
    path('api/cabang/list/', views.api_list_cabang, name='api_list_cabang'),

    # ============================================================
    # API - MODE JAM KERJA
    # ============================================================
    path('api/mode/<int:pk>/jadwal/', views.api_get_mode_jadwal, name='api_mode_jadwal'),
    path('api/mode/<int:pk>/get-jam-kerja-groups/', views.api_get_jam_kerja_groups, name='api_get_jam_kerja_groups'),
    path('api/mode/<int:pk>/pegawai-list/', views.api_get_mode_pegawai_list, name='api_get_mode_pegawai_list'),
    path('api/mode/<int:pk>/periode-list/', views.api_get_mode_periode_list, name='api_get_mode_periode_list'),
    path('api/mode-assignment-form/<int:pegawai_id>/', views.api_get_mode_assignment_form, name='api_get_mode_assignment_form'),
    path('api/save-mode-assignment-bulk/', views.api_save_mode_assignment_bulk, name='api_save_mode_assignment_bulk'),
    path('api/batalkan-pegawai-pending/', views.batalkan_pegawai_pending, name='batalkan_pegawai_pending'),
]