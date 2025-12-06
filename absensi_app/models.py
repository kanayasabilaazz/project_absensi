from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta


# ==============================================================================
# MASTER DATA ORGANISASI
# ==============================================================================

class MasterDepartemen(models.Model):
    """Departemen/Divisi perusahaan"""
    
    nama = models.CharField(max_length=100, unique=True)
    id_departemen = models.CharField(max_length=5, unique=True, null=True, blank=True, verbose_name="ID Departemen")
    keterangan = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'master_departemen'
        ordering = ['id_departemen', 'nama']
        verbose_name = 'Departemen'
        verbose_name_plural = 'Departemen'
        indexes = [models.Index(fields=['id_departemen'])]
    
    def __str__(self):
        return f"{self.id_departemen} - {self.nama}"
    
    def generate_next_userid(self):
        """Generate User ID berikutnya: id_departemen + nomor urut"""
        last_pegawai = self.pegawai_list.filter(
            userid__startswith=self.id_departemen
        ).order_by('-userid').first()
        
        if last_pegawai:
            try:
                nomor_part = last_pegawai.userid[len(self.id_departemen):]
                next_number = int(nomor_part) + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{self.id_departemen}{str(next_number).zfill(2)}"
    
    def get_jumlah_pegawai(self):
        """Hitung total pegawai aktif"""
        return self.pegawai_list.filter(is_active=True).count()


class MasterJabatan(models.Model):
    """Jabatan pegawai"""
    
    nama = models.CharField(max_length=100, unique=True)
    kode = models.CharField(max_length=20, unique=True)
    keterangan = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'master_jabatan'
        ordering = ['nama']
        verbose_name = 'Jabatan'
        verbose_name_plural = 'Jabatan'
    
    def __str__(self):
        return f"{self.kode} - {self.nama}"


class MasterCabang(models.Model):
    """Cabang/Lokasi kerja"""
    
    nama = models.CharField(max_length=100, unique=True)
    kode = models.CharField(max_length=20, unique=True)
    alamat = models.TextField()
    ip_mesin_fingerprint = models.TextField(blank=True, help_text="Daftar IP mesin, pisahkan dengan koma")
    port_mesin = models.IntegerField(default=4370)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'master_cabang'
        ordering = ['nama']
        verbose_name = 'Cabang'
        verbose_name_plural = 'Cabang'

    def __str__(self):
        return f"{self.kode} - {self.nama}"
    
    def get_ip_list(self):
        """Ambil daftar IP mesin dalam bentuk list"""
        if not self.ip_mesin_fingerprint:
            return []
        return [ip.strip() for ip in self.ip_mesin_fingerprint.split(',') if ip.strip()]


# ==============================================================================
# MASTER DATA MESIN ABSENSI
# ==============================================================================

class MasterMesin(models.Model):
    """Mesin absensi fingerprint/face recognition"""
    
    nama = models.CharField(max_length=100)
    kode = models.CharField(max_length=20, unique=True)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=4370)
    lokasi = models.CharField(max_length=200, blank=True)
    keterangan = models.TextField(blank=True)
    cabang = models.ForeignKey(MasterCabang, on_delete=models.CASCADE, related_name='mesin')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'master_mesin'
        ordering = ['cabang', 'nama']
        verbose_name = 'Mesin Absensi'
        verbose_name_plural = 'Mesin Absensi'
        unique_together = ['cabang', 'nama']
    
    def __str__(self):
        return f"{self.nama} ({self.ip_address})"


# ==============================================================================
# MASTER DATA MODE JAM KERJA
# ==============================================================================

class MasterModeJamKerja(models.Model):
    """Mode jam kerja dengan prioritas dan periode"""
    
    PRIORITY_CHOICES = [(1, 'Low'), (2, 'Medium'), (3, 'High')]
    
    nama = models.CharField(max_length=100, unique=True)
    kode = models.CharField(max_length=20, unique=True)
    warna = models.CharField(max_length=7, default='#3B82F6')
    icon = models.CharField(max_length=50, default='fas fa-clock')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'master_mode_jam_kerja'
        verbose_name = 'Mode Jam Kerja'
        verbose_name_plural = 'Mode Jam Kerja'
        ordering = ['-priority', 'nama']
        indexes = [
            models.Index(fields=['is_default', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.nama}{' (Default)' if self.is_default else ''}"
    
    def save(self, *args, **kwargs):
        """Pastikan hanya ada satu mode default"""
        if self.is_default:
            MasterModeJamKerja.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_jadwal_hari(self, hari):
        """Ambil jadwal untuk hari tertentu (0=Senin, 6=Minggu)"""
        return self.jadwal_list.filter(hari=hari).first()
    
    def has_schedule_for_day(self, hari):
        """Cek ketersediaan jadwal untuk hari tertentu"""
        return self.jadwal_list.filter(hari=hari).exists()
    
    def get_total_pegawai(self):
        """Hitung total pegawai yang menggunakan mode ini"""
        return self.pegawai_list.filter(is_active=True).count()
    
    def get_active_periode(self):
        """Ambil periode yang sedang aktif hari ini"""
        today = date.today()
        return self.periode_list.filter(
            is_active=True,
            tanggal_mulai__lte=today,
            tanggal_selesai__gte=today
        ).first()
    
    def is_applicable_today(self):
        """Cek apakah mode ini berlaku hari ini"""
        periode_aktif = self.get_active_periode()
        return periode_aktif is not None or self.is_default


class ModeJamKerjaJadwal(models.Model):
    """Jadwal jam kerja per grup shift"""
    
    HARI_CHOICES = [
        (0, 'Senin'), (1, 'Selasa'), (2, 'Rabu'), (3, 'Kamis'),
        (4, 'Jumat'), (5, 'Sabtu'), (6, 'Minggu')
    ]
    
    mode = models.ForeignKey(MasterModeJamKerja, on_delete=models.CASCADE, related_name='jadwal_list')
    group_name = models.CharField(max_length=100, verbose_name="Nama Grup")
    hari = models.IntegerField(choices=HARI_CHOICES)
    jam_masuk = models.TimeField(null=True, blank=True)
    jam_keluar = models.TimeField(null=True, blank=True)
    jam_istirahat_keluar = models.TimeField(null=True, blank=True)
    jam_istirahat_masuk = models.TimeField(null=True, blank=True)
    toleransi_terlambat = models.IntegerField(default=15, verbose_name="Toleransi Terlambat (menit)")
    toleransi_pulang_cepat = models.IntegerField(default=15, verbose_name="Toleransi Pulang Cepat (menit)")
    urutan = models.IntegerField(default=1, verbose_name="Urutan Shift")
    
    class Meta:
        db_table = 'mode_jam_kerja_jadwal'
        verbose_name = 'Jadwal Mode'
        verbose_name_plural = 'Jadwal Mode'
        unique_together = ['mode', 'group_name', 'hari']
        ordering = ['mode', 'group_name', 'hari', 'urutan']
        indexes = [
            models.Index(fields=['mode', 'hari']),
            models.Index(fields=['mode', 'group_name', 'hari']),
        ]
    
    def __str__(self):
        hari_nama = dict(self.HARI_CHOICES)[self.hari]
        return f"{self.mode.nama} - {self.group_name} ({hari_nama})"
    
    def get_jam_kerja_display(self):
        """Format jam kerja untuk tampilan"""
        if not self.jam_masuk or not self.jam_keluar:
            return "Belum diatur"
        return f"{self.jam_masuk.strftime('%H:%M')} - {self.jam_keluar.strftime('%H:%M')}"
    
    def get_duration_minutes(self):
        """Hitung durasi kerja dalam menit (tanpa waktu istirahat)"""
        if not self.jam_masuk or not self.jam_keluar:
            return None
        
        today = date.today()
        dt_masuk = datetime.combine(today, self.jam_masuk)
        dt_keluar = datetime.combine(today, self.jam_keluar)
        
        if dt_keluar < dt_masuk:
            dt_keluar += timedelta(days=1)
        
        total_minutes = int((dt_keluar - dt_masuk).total_seconds() / 60)
        
        if self.jam_istirahat_keluar and self.jam_istirahat_masuk:
            dt_break_out = datetime.combine(today, self.jam_istirahat_keluar)
            dt_break_in = datetime.combine(today, self.jam_istirahat_masuk)
            
            if dt_break_in < dt_break_out:
                dt_break_in += timedelta(days=1)
            
            break_minutes = int((dt_break_in - dt_break_out).total_seconds() / 60)
            total_minutes -= break_minutes
        
        return total_minutes
    
    def get_duration_formatted(self):
        """Format durasi kerja: 8j 30m"""
        duration = self.get_duration_minutes()
        if not duration:
            return None
        
        hours = duration // 60
        minutes = duration % 60
        return f"{hours}j {minutes}m" if hours > 0 else f"{minutes}m"


class ModeJamKerjaPeriode(models.Model):
    """Periode aktif untuk mode tertentu"""
    
    mode = models.ForeignKey(MasterModeJamKerja, on_delete=models.CASCADE, related_name='periode_list')
    nama = models.CharField(max_length=100, verbose_name="Nama Periode")
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    tahun = models.IntegerField()
    catatan = models.TextField(blank=True)
    warna_periode = models.CharField(max_length=7, blank=True, help_text='Warna untuk laporan (opsional)')
    is_periode_khusus = models.BooleanField(default=False, help_text='Periode khusus')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mode_jam_kerja_periode'
        verbose_name = 'Periode Mode'
        verbose_name_plural = 'Periode Mode'
        ordering = ['-tanggal_mulai']
        indexes = [
            models.Index(fields=['tanggal_mulai', 'tanggal_selesai']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        status = " (Khusus)" if self.is_periode_khusus else ""
        return f"{self.nama}{status} ({self.tanggal_mulai} - {self.tanggal_selesai})"
    
    def is_active_today(self):
        """Cek apakah periode ini aktif hari ini"""
        today = date.today()
        return self.is_active and self.tanggal_mulai <= today <= self.tanggal_selesai
    
    def get_duration_days(self):
        """Hitung durasi periode dalam hari"""
        return (self.tanggal_selesai - self.tanggal_mulai).days + 1


# ==============================================================================
# DATA PEGAWAI
# ==============================================================================

class Pegawai(models.Model):
    """Data karyawan dalam sistem absensi"""
    
    userid = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="User ID")
    nama_lengkap = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(blank=True, null=True)
    nomor_hp = models.CharField(max_length=15, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    
    # Relasi Organisasi
    departemen = models.ForeignKey(MasterDepartemen, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai_list')
    jabatan = models.ForeignKey(MasterJabatan, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai_list')
    cabang = models.ForeignKey(MasterCabang, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai_list')
    
    # Jam Kerja
    mode_jam_kerja = models.ForeignKey(MasterModeJamKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai_list')
    jam_kerja_assignment = models.JSONField(default=dict, blank=True)
    
    # Mesin & UID
    mesin = models.ForeignKey(MasterMesin, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai_list')
    uid_mesin = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="UID di Mesin")
    
    # Status & Tanggal
    shift_per_hari = models.JSONField(default=dict, blank=True)
    tanggal_bergabung = models.DateField(null=True, blank=True)
    tanggal_nonaktif = models.DateField(null=True, blank=True)
    is_shift_worker = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'absensi_app_pegawai'
        ordering = ['userid']
        verbose_name = 'Pegawai'
        verbose_name_plural = 'Pegawai'
        indexes = [
            models.Index(fields=['userid']),
            models.Index(fields=['cabang', 'userid']),
            models.Index(fields=['departemen', 'is_shift_worker']),
        ]
    
    def __str__(self):
        return f"{self.userid} - {self.nama_lengkap}"
    
    @property
    def is_registered_in_machine(self):
        """Cek status registrasi di mesin fingerprint"""
        return self.uid_mesin is not None and self.uid_mesin > 0
    
    def get_fingerprint_count(self):
        """Hitung jumlah template fingerprint tersimpan"""
        return self.fingerprint_templates.count()


class FingerprintTemplate(models.Model):
    """Template sidik jari dari mesin absensi"""
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='fingerprint_templates')
    uid = models.IntegerField()
    fid = models.IntegerField()
    size = models.IntegerField()
    valid = models.IntegerField()
    template = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'absensi_app_fingerprinttemplate'
        unique_together = ['pegawai', 'fid']
        ordering = ['pegawai', 'fid']

    def __str__(self):
        return f"{self.pegawai.nama_lengkap} - Finger {self.fid}"


class PegawaiModeAssignment(models.Model):
    """Assignment jadwal jam kerja pegawai per mode"""
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='mode_assignments')
    mode = models.ForeignKey(MasterModeJamKerja, on_delete=models.CASCADE, related_name='pegawai_assignments')
    jadwal_per_hari = models.JSONField(default=dict, verbose_name="Jadwal Per Hari")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pegawai_mode_assignment'
        unique_together = ['pegawai', 'mode']
        indexes = [models.Index(fields=['pegawai', 'mode'])]
    
    def __str__(self):
        return f"{self.pegawai.nama_lengkap} - {self.mode.nama}"
    
    def get_jadwal_hari(self, hari):
        """Ambil jadwal untuk hari tertentu (0-6)"""
        jadwal_id = self.jadwal_per_hari.get(str(hari))
        if jadwal_id:
            try:
                return ModeJamKerjaJadwal.objects.get(id=jadwal_id)
            except ModeJamKerjaJadwal.DoesNotExist:
                pass
        return None


# ==============================================================================
# DATA ABSENSI (LEGACY)
# ==============================================================================

class Absensi(models.Model):
    """Model catatan absensi harian pegawai (LEGACY)"""
    
    STATUS_CHOICES = [('Hadir', 'Hadir'), ('Sakit', 'Sakit'), ('Izin', 'Izin'), ('Absen', 'Absen')]

    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='absensi')
    tanggal = models.DateField()
    tap_masuk = models.TimeField(null=True, blank=True)
    tap_pulang = models.TimeField(null=True, blank=True)
    tap_istirahat_keluar = models.TimeField(null=True, blank=True)
    tap_istirahat_masuk = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    is_late = models.BooleanField(default=False)
    is_early_departure = models.BooleanField(default=False)
    keterangan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'absensi_app_absensi'
        unique_together = ['pegawai', 'tanggal']
        ordering = ['-tanggal', '-tap_masuk']
        indexes = [
            models.Index(fields=['tanggal', 'status']),
            models.Index(fields=['pegawai', 'tanggal']),
        ]

    def __str__(self):
        return f"{self.pegawai.nama_lengkap} - {self.tanggal} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-hitung keterlambatan saat save"""
        if self.status == 'Hadir' and self.tap_masuk:
            self.hitung_status_keterlambatan()
        super().save(*args, **kwargs)
    
    def hitung_status_keterlambatan(self):
        """Hitung status keterlambatan dan pulang cepat"""
        if not self.tap_masuk:
            return
        
        from .services import WorkModeService
        jam_kerja_info = WorkModeService.get_jam_kerja_for_pegawai(self.pegawai, self.tanggal)
        
        if not jam_kerja_info or not jam_kerja_info.get('jadwal'):
            return
        
        jadwal = jam_kerja_info['jadwal']
        is_hari_kerja = jadwal.jam_masuk is not None and jadwal.jam_keluar is not None
        
        if not is_hari_kerja:
            return
        
        # Cek keterlambatan
        if jadwal.jam_masuk:
            tap_masuk_standar = datetime.combine(self.tanggal, jadwal.jam_masuk)
            tap_masuk_actual = datetime.combine(self.tanggal, self.tap_masuk)
            toleransi = timedelta(minutes=jadwal.toleransi_terlambat)
            self.is_late = tap_masuk_actual > tap_masuk_standar + toleransi
        
        # Cek pulang cepat
        if self.tap_pulang and jadwal.jam_keluar:
            tap_pulang_standar = datetime.combine(self.tanggal, jadwal.jam_keluar)
            tap_pulang_actual = datetime.combine(self.tanggal, self.tap_pulang)
            toleransi_keluar = timedelta(minutes=jadwal.toleransi_pulang_cepat)
            self.is_early_departure = tap_pulang_actual < tap_pulang_standar - toleransi_keluar
        else:
            self.is_early_departure = False
    
    def calculate_total_jam_kerja(self):
        """Hitung total jam kerja dengan pengurangan waktu istirahat"""
        if not self.tap_masuk or not self.tap_pulang:
            return {
                'hours': 0,
                'minutes': 0,
                'total_minutes': 0,
                'formatted': '-',
                'has_break': False
            }

        dt_masuk = datetime.combine(self.tanggal, self.tap_masuk)
        dt_keluar = datetime.combine(self.tanggal, self.tap_pulang)

        if dt_keluar < dt_masuk:
            dt_keluar += timedelta(days=1)

        total_minutes = int((dt_keluar - dt_masuk).total_seconds() / 60)
        has_break = False

        # Kurangi waktu istirahat
        if self.tap_istirahat_keluar and self.tap_istirahat_masuk:
            dt_break_out = datetime.combine(self.tanggal, self.tap_istirahat_keluar)
            dt_break_in = datetime.combine(self.tanggal, self.tap_istirahat_masuk)
            if dt_break_in < dt_break_out:
                dt_break_in += timedelta(days=1)
            break_minutes = int((dt_break_in - dt_break_out).total_seconds() / 60)
            total_minutes -= break_minutes
            has_break = True
        else:
            # Default istirahat 2 jam jika tidak ada data
            total_minutes -= 120
            has_break = False

        hours = total_minutes // 60
        minutes = total_minutes % 60
        formatted = f"{hours}j {minutes}m" if hours > 0 else f"{minutes}m"

        return {
            'hours': hours,
            'minutes': minutes,
            'total_minutes': total_minutes,
            'formatted': formatted,
            'has_break': has_break
        }
    
    def get_tap_masuk_display(self):
        """Tampilan tap masuk dengan warna dari MODE pegawai"""
        if not self.tap_masuk:
            return None
        
        mode = self.pegawai.mode_jam_kerja
        if not mode:
            return {
                'is_late': False,
                'is_mode_custom': False,
                'mode_color': None,
                'mode_name': None
            }
        
        is_late = False
        jam_kerja_info = self._get_jam_kerja_for_tanggal(self.tanggal)
        
        if jam_kerja_info and jam_kerja_info.get('jam_masuk'):
            tap_datetime = datetime.combine(self.tanggal, self.tap_masuk)
            expected_datetime = datetime.combine(self.tanggal, jam_kerja_info['jam_masuk'])
            tolerance_delta = timedelta(minutes=jam_kerja_info.get('tolerance', 15))
            is_late = tap_datetime > (expected_datetime + tolerance_delta)
        
        return {
            'is_late': is_late,
            'is_mode_custom': mode.warna != '#3B82F6',
            'mode_color': mode.warna,
            'mode_name': mode.nama
        }
    
    def get_tap_pulang_display(self):
        """Tampilan tap pulang dengan warna dari MODE pegawai"""
        if not self.tap_pulang:
            return None
        
        mode = self.pegawai.mode_jam_kerja
        if not mode:
            return {
                'is_early': False,
                'is_mode_custom': False,
                'mode_color': None,
                'mode_name': None
            }
        
        is_early = False
        jam_kerja_info = self._get_jam_kerja_for_tanggal(self.tanggal)
        
        if jam_kerja_info and jam_kerja_info.get('jam_pulang'):
            tap_datetime = datetime.combine(self.tanggal, self.tap_pulang)
            expected_datetime = datetime.combine(self.tanggal, jam_kerja_info['jam_pulang'])
            is_early = tap_datetime < expected_datetime
        
        return {
            'is_early': is_early,
            'is_mode_custom': mode.warna != '#3B82F6',
            'mode_color': mode.warna,
            'mode_name': mode.nama
        }
    
    def get_total_jam_kerja_display(self):
        """Tampilan total jam kerja dengan warna dari MODE"""
        total_jam = self.calculate_total_jam_kerja()
        mode = self.pegawai.mode_jam_kerja
        
        has_violation = False
        if self.tap_masuk and self.tap_pulang:
            if not self.tap_istirahat_keluar or not self.tap_istirahat_masuk:
                has_violation = True
        
        return {
            'value': total_jam['formatted'] if total_jam else '-',
            'has_violation': has_violation,
            'is_mode_custom': mode and mode.warna != '#3B82F6',
            'mode_color': mode.warna if mode else None,
            'mode_name': mode.nama if mode else None
        }
    
    def get_istirahat_display_with_styling(self):
        """Display waktu istirahat dengan styling untuk UI"""
        default_display = {
            'value': None,
            'class': 'jam-text',
            'is_missing': False,
            'is_auto': False,
            'is_mode_custom': False
        }
        
        keluar_display = default_display.copy()
        masuk_display = default_display.copy()
        
        if self.status != 'Hadir' or not self.tap_masuk or not self.tap_pulang:
            return {'keluar': keluar_display, 'masuk': masuk_display}
        
        mode = self.pegawai.mode_jam_kerja
        is_mode_custom = mode and mode.warna != '#3B82F6'
        mode_color = mode.warna if mode else None
        
        has_keluar = bool(self.tap_istirahat_keluar)
        has_masuk = bool(self.tap_istirahat_masuk)
        
        if has_keluar and has_masuk:
            # Kedua tap ada
            keluar_display = {
                'value': self.tap_istirahat_keluar.strftime('%H:%M'),
                'class': 'jam-text',
                'is_missing': False,
                'is_auto': False,
                'is_mode_custom': is_mode_custom,
                'mode_color': mode_color
            }
            masuk_display = {
                'value': self.tap_istirahat_masuk.strftime('%H:%M'),
                'class': 'jam-text',
                'is_missing': False,
                'is_auto': False,
                'is_mode_custom': is_mode_custom,
                'mode_color': mode_color
            }
        elif has_keluar and not has_masuk:
            # Hanya tap keluar
            keluar_display = {
                'value': self.tap_istirahat_keluar.strftime('%H:%M'),
                'class': 'jam-text',
                'is_missing': False,
                'is_auto': False,
                'is_mode_custom': is_mode_custom,
                'mode_color': mode_color
            }
            masuk_display = {
                'value': '14:00',
                'class': 'jam-text violation',
                'is_missing': True,
                'is_auto': True,
                'is_mode_custom': False,
                'mode_color': None
            }
        elif not has_keluar and has_masuk:
            # Hanya tap masuk
            keluar_display = {
                'value': '12:00',
                'class': 'jam-text violation',
                'is_missing': True,
                'is_auto': True,
                'is_mode_custom': False,
                'mode_color': None
            }
            masuk_display = {
                'value': self.tap_istirahat_masuk.strftime('%H:%M'),
                'class': 'jam-text',
                'is_missing': False,
                'is_auto': False,
                'is_mode_custom': is_mode_custom,
                'mode_color': mode_color
            }
        else:
            # Kedua tap tidak ada
            keluar_display = {
                'value': '12:00',
                'class': 'jam-text violation',
                'is_missing': True,
                'is_auto': True,
                'is_mode_custom': False,
                'mode_color': None
            }
            masuk_display = {
                'value': '14:00',
                'class': 'jam-text violation',
                'is_missing': True,
                'is_auto': True,
                'is_mode_custom': False,
                'mode_color': None
            }
        
        return {'keluar': keluar_display, 'masuk': masuk_display}
    
    def _get_jam_kerja_for_tanggal(self, tanggal):
        """Helper: Ambil jam kerja untuk tanggal tertentu"""
        mode = self.pegawai.mode_jam_kerja
        if not mode:
            return None
        
        hari_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        hari = tanggal.strftime('%A').lower()
        hari_index = hari_mapping.get(hari)
        
        if hari_index is None:
            return None
        
        # Cek assignment khusus pegawai
        if self.pegawai.jam_kerja_assignment:
            jadwal_id = self.pegawai.jam_kerja_assignment.get(str(hari_index))
            if jadwal_id:
                try:
                    jadwal = ModeJamKerjaJadwal.objects.get(id=jadwal_id)
                    return {
                        'jam_masuk': jadwal.jam_masuk,
                        'jam_pulang': jadwal.jam_keluar,
                        'tolerance': jadwal.toleransi_terlambat
                    }
                except ModeJamKerjaJadwal.DoesNotExist:
                    pass
        
        # Fallback ke jadwal default mode
        jadwal = ModeJamKerjaJadwal.objects.filter(
            mode=mode,
            hari=hari_index
        ).first()
        
        if not jadwal:
            return None
        
        return {
            'jam_masuk': jadwal.jam_masuk,
            'jam_pulang': jadwal.jam_keluar,
            'tolerance': jadwal.toleransi_terlambat
        }


# ==============================================================================
# TAP LOG & SESI ABSENSI (NEW)
# ==============================================================================

class TapLog(models.Model):
    """Log setiap tap dari mesin absensi"""
    
    PUNCH_TYPE_CHOICES = [
        (0, 'Masuk'), (1, 'Keluar'),
        (2, 'Istirahat Keluar'), (3, 'Istirahat Masuk')
    ]
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='tap_logs')
    tanggal = models.DateField(db_index=True)
    waktu_tap = models.TimeField()
    punch_type = models.IntegerField(choices=PUNCH_TYPE_CHOICES, default=0)
    mesin = models.ForeignKey(MasterMesin, on_delete=models.SET_NULL, null=True, blank=True, related_name='tap_logs')
    is_processed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tap_log'
        ordering = ['tanggal', 'waktu_tap']
        indexes = [
            models.Index(fields=['pegawai', 'tanggal']),
            models.Index(fields=['pegawai', 'tanggal', 'is_processed']),
            models.Index(fields=['tanggal', 'is_processed']),
        ]
    
    def __str__(self):
        return f"{self.pegawai.nama_lengkap} - {self.tanggal} {self.waktu_tap} ({self.get_punch_type_display()})"
    
    def get_datetime(self):
        """Gabungkan tanggal dan waktu tap"""
        return datetime.combine(self.tanggal, self.waktu_tap)


class AbsensiSesi(models.Model):
    """Sesi kerja pegawai (mendukung multiple shift per hari)"""
    
    STATUS_CHOICES = [('Hadir', 'Hadir'), ('Incomplete', 'Incomplete')]
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sesi_kerja')
    tanggal_mulai = models.DateField(db_index=True)
    tanggal_selesai = models.DateField(db_index=True)
    
    # Tap Masuk
    tap_masuk_pertama = models.TimeField()
    tap_masuk_terakhir = models.TimeField(null=True, blank=True)
    jumlah_tap_masuk = models.IntegerField(default=0)
    
    # Tap Pulang
    tap_pulang_pertama = models.TimeField(null=True, blank=True)
    tap_pulang_terakhir = models.TimeField(null=True, blank=True)
    jumlah_tap_pulang = models.IntegerField(default=0)
    
    # Status & Info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Incomplete')
    is_cross_day = models.BooleanField(default=False, verbose_name="Lintas Hari")
    durasi_kerja_menit = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'absensi_sesi'
        ordering = ['tanggal_mulai', 'tap_masuk_pertama']
        indexes = [
            models.Index(fields=['pegawai', 'tanggal_mulai']),
            models.Index(fields=['tanggal_mulai', 'status']),
        ]
    
    def __str__(self):
        masuk = self.tap_masuk_pertama.strftime('%H:%M')
        pulang = self.tap_pulang_terakhir.strftime('%H:%M') if self.tap_pulang_terakhir else '?'
        return f"{self.pegawai.nama_lengkap} - {self.tanggal_mulai} ({masuk}-{pulang})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate saat save"""
        if self.tap_pulang_terakhir:
            dt_masuk = datetime.combine(self.tanggal_mulai, self.tap_masuk_pertama)
            dt_pulang = datetime.combine(self.tanggal_selesai, self.tap_pulang_terakhir)
            
            self.is_cross_day = self.tanggal_selesai > self.tanggal_mulai
            self.durasi_kerja_menit = int((dt_pulang - dt_masuk).total_seconds() / 60)
            
            if self.status == 'Incomplete':
                self.status = 'Hadir'
        
        super().save(*args, **kwargs)
    
    def get_durasi_formatted(self):
        """Format durasi kerja: 8j 30m"""
        if not self.durasi_kerja_menit:
            return '-'
        hours = self.durasi_kerja_menit // 60
        minutes = self.durasi_kerja_menit % 60
        return f"{hours}j {minutes}m" if hours > 0 else f"{minutes}m"
    
    def get_tap_masuk_display(self):
        """Display tap masuk dengan info multiple tap"""
        if self.jumlah_tap_masuk > 1:
            return f"{self.tap_masuk_pertama.strftime('%H:%M')} ({self.jumlah_tap_masuk}x)"
        return self.tap_masuk_pertama.strftime('%H:%M')
    
    def get_tap_pulang_display(self):
        """Display tap pulang dengan info multiple tap"""
        if not self.tap_pulang_terakhir:
            return '-'
        if self.jumlah_tap_pulang > 1:
            return f"{self.tap_pulang_terakhir.strftime('%H:%M')} ({self.jumlah_tap_pulang}x)"
        return self.tap_pulang_terakhir.strftime('%H:%M')


class TapSesiRelation(models.Model):
    """Relasi antara TapLog dengan AbsensiSesi"""
    
    tap_log = models.ForeignKey(TapLog, on_delete=models.CASCADE, related_name='sesi_relation')
    absensi_sesi = models.ForeignKey(AbsensiSesi, on_delete=models.CASCADE, related_name='tap_relation')
    urutan_dalam_sesi = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tap_sesi_relation'
        unique_together = ['tap_log', 'absensi_sesi']
        ordering = ['absensi_sesi', 'urutan_dalam_sesi']
    
    def __str__(self):
        return f"Tap #{self.tap_log.id} → Sesi #{self.absensi_sesi.id}"