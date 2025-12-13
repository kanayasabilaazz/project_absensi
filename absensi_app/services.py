from datetime import date, timedelta, datetime
from django.core.cache import cache
from django.db import transaction
from collections import defaultdict

# ============================================================
# MODE JAM KERJA SERVICE
# ============================================================

class LayananModeKerja:
    """
    Mengelola mode jam kerja pegawai:
    - Mode aktif berdasarkan tanggal
    - Jadwal jam kerja pegawai
    - Cache management untuk performa
    """
    
    CACHE_TIMEOUT = 3600
    
    @classmethod
    def ambil_mode_aktif(cls, tanggal=None):
        """
        Ambil mode aktif untuk tanggal tertentu
        
        Returns:
            dict: {mode, periode, dari_periode}
        """
        if tanggal is None:
            tanggal = date.today()
        
        cache_key = f'active_mode_{tanggal}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import MasterModeJamKerja, ModeJamKerjaPeriode
        
        # Cari periode aktif
        periode = ModeJamKerjaPeriode.objects.filter(
            is_active=True,
            tanggal_mulai__lte=tanggal,
            tanggal_selesai__gte=tanggal
        ).select_related('mode').order_by(
            '-mode__priority', 
            '-tanggal_mulai'
        ).first()
        
        if periode:
            result = {
                'mode': periode.mode,
                'periode': periode,
                'dari_periode': True
            }
        else:
            # Fallback ke mode default
            mode = MasterModeJamKerja.objects.filter(
                is_default=True,
                is_active=True
            ).first()
            
            # Jika tidak ada default, ambil priority tertinggi
            if not mode:
                mode = MasterModeJamKerja.objects.filter(
                    is_active=True
                ).order_by('-priority', 'nama').first()
            
            result = {
                'mode': mode,
                'periode': None,
                'dari_periode': False
            }
        
        cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result
    
    @classmethod
    def ambil_jadwal_pegawai(cls, pegawai, tanggal=None):
        """
        Ambil jadwal jam kerja pegawai pada tanggal tertentu
        
        Returns:
            dict: {mode, periode, jadwal, is_hari_kerja}
        """
        if tanggal is None:
            tanggal = date.today()
        
        cache_key = f'jadwal_{pegawai.id}_{tanggal}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import ModeJamKerjaJadwal, PegawaiModeAssignment
        
        mode_info = cls.ambil_mode_aktif(tanggal)
        mode = mode_info['mode']
        periode = mode_info['periode']
        
        if not mode:
            return {
                'mode': None,
                'periode': None,
                'jadwal': None,
                'is_hari_kerja': False
            }
        
        # Cari jadwal spesifik pegawai
        hari = tanggal.weekday()
        jadwal = None
        
        assignment = PegawaiModeAssignment.objects.filter(
            pegawai=pegawai,
            mode=mode,
            is_active=True
        ).first()
        
        if assignment and assignment.jadwal_per_hari:
            jadwal_id = assignment.jadwal_per_hari.get(str(hari))
            if jadwal_id:
                try:
                    jadwal = ModeJamKerjaJadwal.objects.get(id=jadwal_id)
                except ModeJamKerjaJadwal.DoesNotExist:
                    pass
        
        # Fallback ke jadwal default mode
        if not jadwal:
            jadwal = ModeJamKerjaJadwal.objects.filter(
                mode=mode,
                hari=hari
            ).order_by('urutan', 'group_name').first()
        
        result = {
            'mode': mode,
            'periode': periode,
            'jadwal': jadwal,
            'is_hari_kerja': bool(jadwal and jadwal.jam_masuk and jadwal.jam_keluar)
        }
        
        cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result
    
    @classmethod
    def cek_hari_kerja(cls, pegawai, tanggal=None):
        """Cek apakah tanggal adalah hari kerja"""
        jadwal = cls.ambil_jadwal_pegawai(pegawai, tanggal)
        return jadwal['is_hari_kerja']
    
    @classmethod
    def info_mode_hari_ini(cls):
        """Info mode hari ini untuk template"""
        mode_info = cls.ambil_mode_aktif()
        
        if not mode_info['mode']:
            return {
                'nama_mode': 'Tidak Ada Mode',
                'kode_mode': 'N/A',
                'warna_mode': '#999999',
                'icon_mode': 'fas fa-exclamation-triangle',
                'nama_periode': None,
                'is_libur': True,
            }
        
        mode = mode_info['mode']
        periode = mode_info['periode']
        
        return {
            'nama_mode': mode.nama,
            'kode_mode': mode.kode,
            'warna_mode': mode.warna,
            'icon_mode': mode.icon,
            'nama_periode': periode.nama if periode else None,
            'is_libur': False,
        }
    
    @classmethod
    def info_mode_untuk_tanggal(cls, tanggal):
        """Info mode untuk tanggal tertentu (riwayat absensi)"""
        mode_info = cls.ambil_mode_aktif(tanggal)
        
        if not mode_info['mode']:
            return {
                'nama_mode': 'Tidak Ada Mode',
                'kode_mode': 'N/A',
                'warna_mode': '#999999',
                'icon_mode': 'fas fa-exclamation-triangle',
                'nama_periode': None,
                'is_libur': True,
                'is_mode_khusus': False
            }
        
        mode = mode_info['mode']
        periode = mode_info['periode']
        
        return {
            'nama_mode': mode.nama,
            'kode_mode': mode.kode,
            'warna_mode': mode.warna,
            'icon_mode': mode.icon,
            'nama_periode': periode.nama if periode else None,
            'is_libur': False,
            'is_mode_khusus': periode is not None
        }
    
    @classmethod
    def bersihkan_cache(cls, tanggal_mulai=None, tanggal_selesai=None):
        """Bersihkan cache untuk range tanggal"""
        if tanggal_mulai and tanggal_selesai:
            current = tanggal_mulai
            while current <= tanggal_selesai:
                cache.delete(f'active_mode_{current}')
                current += timedelta(days=1)
        else:
            cache.clear()
    
    @classmethod
    def get_upcoming_modes(cls, days=30):
        """Periode yang akan datang dalam N hari"""
        from .models import ModeJamKerjaPeriode
        
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return ModeJamKerjaPeriode.objects.filter(
            is_active=True,
            tanggal_mulai__gte=today,
            tanggal_mulai__lte=end_date
        ).select_related('mode').order_by('tanggal_mulai')[:10]


# ============================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================

class WorkModeService:
    """Alias untuk LayananModeKerja (backward compatibility)"""
    
    @staticmethod
    def get_active_mode_for_date(tanggal=None):
        result = LayananModeKerja.ambil_mode_aktif(tanggal)
        return {
            'mode': result['mode'],
            'periode': result['periode'],
            'is_from_periode': result['dari_periode']
        } if result else None
    
    @staticmethod
    def get_jam_kerja_for_pegawai(pegawai, tanggal=None):
        return LayananModeKerja.ambil_jadwal_pegawai(pegawai, tanggal)
    
    @staticmethod
    def is_hari_kerja(pegawai, tanggal=None):
        return LayananModeKerja.cek_hari_kerja(pegawai, tanggal)
    
    @staticmethod
    def get_mode_today():
        return LayananModeKerja.info_mode_hari_ini()
    
    @staticmethod
    def get_mode_for_date(tanggal):
        return LayananModeKerja.info_mode_untuk_tanggal(tanggal)
        
    @staticmethod
    def get_upcoming_modes(days=30):
        return LayananModeKerja.get_upcoming_modes(days)
    
    @staticmethod
    def clear_cache(tanggal_mulai=None, tanggal_selesai=None):
        return LayananModeKerja.bersihkan_cache(tanggal_mulai, tanggal_selesai)


# ============================================================
# TAP STACK PROCESSOR - TAP LOG → SESI ABSENSI
# ============================================================

class TapStackProcessor:
    """
    Memproses TapLog menjadi AbsensiSesi menggunakan STACK (LIFO)
    
    Algoritma:
    - TAP MASUK (0) → PUSH ke stack
    - TAP PULANG (1) → POP dari stack → BUAT SESI
    - Multiple TAP MASUK → PUSH multiple times
    - TAP ISTIRAHAT → SKIP
    
    Contoh:
    MASUK-PULANG-MASUK-PULANG-MASUK-MASUK-MASUK-PULANG
    = 3 sesi (MASUK₁→PULANG₁, MASUK₂→PULANG₂, MASUK₃→PULANG₃)
    """
    
    @classmethod
    def proses_semua_tap(cls):
        """
        Proses semua tap yang belum diproses menjadi sesi
        
        Returns:
            dict: {status, total_pegawai, total_sesi, total_tap, detail, message}
        """
        from .models import TapLog, Pegawai
        
        try:
            # Ambil tap yang belum diproses
            unprocessed_taps = TapLog.objects.filter(
                is_processed=False
            ).select_related('pegawai', 'mesin').order_by('tanggal', 'waktu_tap')
            
            if not unprocessed_taps.exists():
                return {
                    'status': 'info',
                    'total_pegawai': 0,
                    'total_sesi': 0,
                    'total_tap': 0,
                    'detail': [],
                    'message': 'ℹ️ Tidak ada tap yang perlu diproses'
                }
            
            # Group by pegawai
            taps_by_pegawai = defaultdict(list)
            for tap in unprocessed_taps:
                taps_by_pegawai[tap.pegawai.id].append(tap)
            
            total_sesi_created = 0
            total_tap_processed = 0
            detail_per_pegawai = []
            
            # Proses per pegawai
            for pegawai_id, tap_list in taps_by_pegawai.items():
                try:
                    pegawai = Pegawai.objects.get(id=pegawai_id)
                    
                    # Group by tanggal
                    taps_by_date = defaultdict(list)
                    for tap in tap_list:
                        taps_by_date[tap.tanggal].append(tap)
                    
                    sesi_count = 0
                    tap_count = 0
                    
                    # Proses per tanggal
                    for tanggal, daily_taps in taps_by_date.items():
                        daily_taps.sort(key=lambda t: t.waktu_tap)
                        
                        sesi_list = cls._proses_tap_dengan_stack(daily_taps)
                        
                        for sesi_data in sesi_list:
                            try:
                                cls._simpan_sesi(pegawai, sesi_data)
                                sesi_count += 1
                                tap_count += len(sesi_data['tap_ids'])
                            except Exception as e:
                                print(f"⚠️ ERROR simpan sesi pegawai {pegawai.userid}: {str(e)}")
                                import traceback
                                traceback.print_exc()
                                continue
                    
                    total_sesi_created += sesi_count
                    total_tap_processed += tap_count
                    
                    detail_per_pegawai.append({
                        'pegawai_id': pegawai.id,
                        'pegawai_nama': pegawai.nama_lengkap,
                        'sesi_count': sesi_count,
                        'tap_count': tap_count
                    })
                    
                except Pegawai.DoesNotExist:
                    print(f"⚠️ Pegawai ID {pegawai_id} tidak ditemukan")
                    continue
                except Exception as e:
                    print(f"⚠️ ERROR processing pegawai {pegawai_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Build response
            if total_sesi_created == 0:
                return {
                    'status': 'info',
                    'total_pegawai': len(taps_by_pegawai),
                    'total_sesi': 0,
                    'total_tap': 0,
                    'detail': detail_per_pegawai,
                    'message': f'ℹ️ Tidak ada sesi yang terbuat\n\nKemungkinan:\n• Tidak ada tap MASUK\n• Tidak ada tap PULANG yang match\n• Hanya ada tap ISTIRAHAT'
                }
            
            return {
                'status': 'success',
                'total_pegawai': len(taps_by_pegawai),
                'total_sesi': total_sesi_created,
                'total_tap': total_tap_processed,
                'detail': detail_per_pegawai,
                'message': f'✅ Berhasil memproses tap menjadi sesi!\n\nDetail:\n• Pegawai: {len(taps_by_pegawai)}\n• Sesi: {total_sesi_created}\n• Tap: {total_tap_processed}'
            }
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ ERROR proses_semua_tap: {error_detail}")
            
            return {
                'status': 'error',
                'total_pegawai': 0,
                'total_sesi': 0,
                'total_tap': 0,
                'detail': [],
                'message': f'❌ Error: {str(e)}'
            }
    
    @classmethod
    def _proses_tap_dengan_stack(cls, tap_list):
        """
        Algoritma STACK untuk proses tap
        
        Logic:
        1. MASUK → PUSH ke stack
        2. MASUK lagi → PUSH lagi (multiple sesi)
        3. PULANG → POP stack terakhir → BUAT SESI
        4. ISTIRAHAT → SKIP
        
        Args:
            tap_list: List TapLog (sorted by waktu_tap)
            
        Returns:
            List[dict]: Sesi data
        """
        stack_masuk = []
        sesi_list = []
        
        for tap in tap_list:
            if tap.punch_type == 0:  
                stack_masuk.append({
                    'tap_masuk': tap,
                    'tap_pulang': None,
                    'all_taps': [tap]
                })
            
            elif tap.punch_type == 1:  # TAP PULANG
                if stack_masuk:
                    sesi_data = stack_masuk.pop()
                    sesi_data['tap_pulang'] = tap
                    sesi_data['all_taps'].append(tap)
                    
                    sesi = cls._buat_sesi_data(sesi_data)
                    sesi_list.append(sesi)
                else:
                    print(f"⚠️ SKIP: Tap PULANG tanpa MASUK ({tap.waktu_tap})")
            
            elif tap.punch_type in [2, 3]: 
                if stack_masuk:
                    stack_masuk[-1]['all_taps'].append(tap)
        
        # Handle sesi incomplete (masuk tapi belum pulang)
        for incomplete in stack_masuk:
            print(f"⚠️ Sesi INCOMPLETE: MASUK {incomplete['tap_masuk'].waktu_tap} (belum pulang)")
            sesi = cls._buat_sesi_data(incomplete)
            sesi_list.append(sesi)
        
        return sesi_list
    
    @classmethod
    def _buat_sesi_data(cls, sesi_data):
        """
        Buat data sesi dari dict yang di-pop dari stack
        
        Args:
            sesi_data: {tap_masuk, tap_pulang, all_taps}
        
        Returns:
            dict: Sesi data untuk database
        """
        tap_masuk = sesi_data['tap_masuk']
        tap_pulang = sesi_data['tap_pulang']
        all_taps = sesi_data['all_taps']
        
        tanggal_masuk = tap_masuk.tanggal
        tanggal_pulang = tap_pulang.tanggal if tap_pulang else tanggal_masuk
        
        is_cross_day = tanggal_pulang > tanggal_masuk
        
        # Hitung durasi kerja
        if tap_pulang:
            dt_masuk = datetime.combine(tanggal_masuk, tap_masuk.waktu_tap)
            dt_pulang = datetime.combine(tanggal_pulang, tap_pulang.waktu_tap)
            durasi_menit = int((dt_pulang - dt_masuk).total_seconds() / 60)
        else:
            durasi_menit = 0
        
        tap_ids = [t.id for t in all_taps]
        jumlah_tap_masuk = sum(1 for t in all_taps if t.punch_type == 0)
        jumlah_tap_pulang = sum(1 for t in all_taps if t.punch_type == 1)
        
        return {
            'tanggal_mulai': tanggal_masuk,
            'tanggal_selesai': tanggal_pulang,
            'tap_masuk_pertama': tap_masuk.waktu_tap,
            'tap_masuk_terakhir': tap_masuk.waktu_tap,
            'jumlah_tap_masuk': jumlah_tap_masuk,
            'tap_pulang_pertama': tap_pulang.waktu_tap if tap_pulang else None,
            'tap_pulang_terakhir': tap_pulang.waktu_tap if tap_pulang else None,
            'jumlah_tap_pulang': jumlah_tap_pulang,
            'is_cross_day': is_cross_day,
            'durasi_kerja_menit': durasi_menit,
            'status': 'Hadir' if tap_pulang else 'Incomplete',
            'tap_ids': tap_ids
        }
    
    @classmethod
    def _simpan_sesi(cls, pegawai, sesi_data):
        """Simpan sesi ke database dengan relasi tap"""
        from .models import AbsensiSesi, TapSesiRelation, TapLog
        
        with transaction.atomic():
            # Buat absensi sesi
            sesi = AbsensiSesi.objects.create(
                pegawai=pegawai,
                tanggal_mulai=sesi_data['tanggal_mulai'],
                tanggal_selesai=sesi_data['tanggal_selesai'],
                tap_masuk_pertama=sesi_data['tap_masuk_pertama'],
                tap_masuk_terakhir=sesi_data['tap_masuk_terakhir'],
                jumlah_tap_masuk=sesi_data['jumlah_tap_masuk'],
                tap_pulang_pertama=sesi_data['tap_pulang_pertama'],
                tap_pulang_terakhir=sesi_data['tap_pulang_terakhir'],
                jumlah_tap_pulang=sesi_data['jumlah_tap_pulang'],
                is_cross_day=sesi_data['is_cross_day'],
                durasi_kerja_menit=sesi_data['durasi_kerja_menit'],
                status=sesi_data['status']
            )
            
            # Buat relasi dengan tap logs
            for idx, tap_id in enumerate(sesi_data['tap_ids'], start=1):
                try:
                    TapSesiRelation.objects.create(
                        tap_log_id=tap_id,
                        absensi_sesi=sesi,
                        urutan_dalam_sesi=idx
                    )
                except Exception as e:
                    print(f"⚠️ ERROR buat relasi tap_id {tap_id}: {str(e)}")
                    raise
            
            # Mark tap sebagai processed
            TapLog.objects.filter(
                id__in=sesi_data['tap_ids']
            ).update(is_processed=True)
    
    @classmethod
    def get_sesi_summary_untuk_pegawai(cls, pegawai, tanggal_mulai, tanggal_akhir):
        """
        Summary sesi pegawai dalam range tanggal
        
        Returns:
            dict: {sesi_list, sesi_per_hari, total_sesi, total_hari_kerja}
        """
        from .models import AbsensiSesi
        
        sesi_list = AbsensiSesi.objects.filter(
            pegawai=pegawai,
            tanggal_mulai__gte=tanggal_mulai,
            tanggal_mulai__lte=tanggal_akhir
        ).order_by('tanggal_mulai', 'tap_masuk_pertama')
        
        # Group by tanggal
        sesi_per_hari = defaultdict(list)
        for sesi in sesi_list:
            sesi_per_hari[sesi.tanggal_mulai].append(sesi)
        
        return {
            'sesi_list': sesi_list,
            'sesi_per_hari': dict(sesi_per_hari),
            'total_sesi': sesi_list.count(),
            'total_hari_kerja': len(sesi_per_hari)
        }