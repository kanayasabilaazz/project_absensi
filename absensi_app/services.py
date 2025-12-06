from datetime import date, timedelta, datetime
from django.core.cache import cache
from django.db import transaction
from collections import defaultdict


# ==============================================================================
# LAYANAN MODE JAM KERJA
# ==============================================================================

class LayananModeKerja:
    """
    Service untuk mengelola mode jam kerja pegawai
    - Ambil mode aktif berdasarkan tanggal
    - Ambil jadwal jam kerja pegawai
    - Manajemen cache untuk performa
    """
    
    CACHE_TIMEOUT = 3600 
    
    @classmethod
    def ambil_mode_aktif(cls, tanggal=None):
        """
        Ambil mode yang aktif untuk tanggal tertentu
        
        Returns:
            dict: {
                'mode': MasterModeJamKerja,
                'periode': ModeJamKerjaPeriode or None,
                'dari_periode': bool
            }
        """
        if tanggal is None:
            tanggal = date.today()
        
        # Cek cache terlebih dahulu
        cache_key = f'active_mode_{tanggal}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import MasterModeJamKerja, ModeJamKerjaPeriode
        
        # 1. Cari periode aktif untuk tanggal ini
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
            # 2. Fallback ke mode default
            mode = MasterModeJamKerja.objects.filter(
                is_default=True,
                is_active=True
            ).first()
            
            # 3. Jika tidak ada default, ambil mode dengan priority tertinggi
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
        Ambil jadwal jam kerja untuk pegawai pada tanggal tertentu
        
        Args:
            pegawai: Instance Pegawai
            tanggal: date object, default today
            
        Returns:
            dict: {
                'mode': MasterModeJamKerja,
                'periode': ModeJamKerjaPeriode or None,
                'jadwal': ModeJamKerjaJadwal or None,
                'is_hari_kerja': bool
            }
        """
        if tanggal is None:
            tanggal = date.today()
        
        # Cek cache
        cache_key = f'jadwal_{pegawai.id}_{tanggal}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        from .models import ModeJamKerjaJadwal, PegawaiModeAssignment
        
        # Ambil mode aktif
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
        
        # Cari jadwal spesifik pegawai (dari assignment)
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
        """Cek apakah tanggal tersebut adalah hari kerja untuk pegawai"""
        jadwal = cls.ambil_jadwal_pegawai(pegawai, tanggal)
        return jadwal['is_hari_kerja']
    
    @classmethod
    def info_mode_hari_ini(cls):
        """
        Ambil informasi mode hari ini untuk ditampilkan di template
        
        Returns:
            dict: Info mode dengan format template-friendly
        """
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
    def bersihkan_cache(cls, tanggal_mulai=None, tanggal_selesai=None):
        """
        Bersihkan cache untuk range tanggal tertentu
        Jika tidak ada parameter, bersihkan semua cache
        """
        if tanggal_mulai and tanggal_selesai:
            current = tanggal_mulai
            while current <= tanggal_selesai:
                cache.delete(f'active_mode_{current}')
                current += timedelta(days=1)
        else:
            cache.clear()
    
    @classmethod
    def get_upcoming_modes(cls, days=30):
        """Ambil periode yang akan datang dalam N hari ke depan"""
        from .models import ModeJamKerjaPeriode
        
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return ModeJamKerjaPeriode.objects.filter(
            is_active=True,
            tanggal_mulai__gte=today,
            tanggal_mulai__lte=end_date
        ).select_related('mode').order_by('tanggal_mulai')[:10]


# ==============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ==============================================================================

class WorkModeService:
    """
    Alias untuk LayananModeKerja (backward compatibility)
    """
    
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
    def get_upcoming_modes(days=30):
        return LayananModeKerja.get_upcoming_modes(days)
    
    @staticmethod
    def clear_cache(tanggal_mulai=None, tanggal_selesai=None):
        return LayananModeKerja.bersihkan_cache(tanggal_mulai, tanggal_selesai)


# ==============================================================================
# TAP STACK PROCESSOR - MEMPROSES TAP LOG → SESI ABSENSI
# ==============================================================================
class TapStackProcessor:
    """
    Service untuk memproses TapLog menjadi AbsensiSesi
    menggunakan algoritma STACK (LIFO - Last In First Out)
    
    Algoritma:
    - TAP MASUK (0) → PUSH ke stack
    - TAP PULANG (1) → POP dari stack → BUAT SESI
    - Multiple TAP MASUK → PUSH multiple times (multiple sesi)
    - TAP ISTIRAHAT → SKIP
    
    Contoh:
    MASUK-PULANG-MASUK-PULANG-MASUK-MASUK-MASUK-PULANG
    = 3 sesi (MASUK₁→PULANG₁, MASUK₂→PULANG₂, MASUK₃→PULANG₃)
    """
    
    @classmethod
    def proses_semua_tap(cls):
        """
        Proses SEMUA tap yang belum diproses menjadi sesi
        
        Returns:
            dict: {
                'status': 'success' | 'info' | 'error',
                'total_pegawai': int,
                'total_sesi': int,
                'total_tap': int,
                'detail': [...],
                'message': str
            }
        """
        from .models import TapLog, Pegawai
        
        try:
            # ========================================
            # 1. AMBIL TAP YANG BELUM DIPROSES
            # ========================================
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
            
            # ========================================
            # 2. GROUP BY PEGAWAI
            # ========================================
            taps_by_pegawai = defaultdict(list)
            for tap in unprocessed_taps:
                taps_by_pegawai[tap.pegawai.id].append(tap)
            
            total_sesi_created = 0
            total_tap_processed = 0
            detail_per_pegawai = []
            
            # ========================================
            # 3. PROSES PER PEGAWAI
            # ========================================
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
                        
                        # ✅ ALGORITMA STACK BARU
                        sesi_list = cls._proses_tap_dengan_stack_v2(daily_taps)
                        
                        # Simpan setiap sesi ke database
                        for sesi_data in sesi_list:
                            try:
                                cls._simpan_sesi(pegawai, sesi_data)
                                sesi_count += 1
                                tap_count += len(sesi_data['tap_ids'])
                            except Exception as e:
                                print(f"⚠️ ERROR simpan sesi untuk pegawai {pegawai.userid}: {str(e)}")
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
            
            # ========================================
            # 4. BUILD RESPONSE MESSAGE
            # ========================================
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
    def _proses_tap_dengan_stack_v2(cls, tap_list):
        """
        ✅ ALGORITMA STACK BARU (Berdasarkan Gambar)
        
        Logic:
        1. MASUK → PUSH ke stack
        2. MASUK lagi → PUSH lagi (stack bertambah)
        3. PULANG → POP stack terakhir → BUAT SESI
        4. ISTIRAHAT → SKIP
        
        Args:
            tap_list: List of TapLog objects (sorted by waktu_tap)
            
        Returns:
            List[dict]: List of sesi data
            
        Example:
            Input:  [MASUK, PULANG, MASUK, PULANG, MASUK, MASUK, MASUK, PULANG]
            Stack:  [M] → [] → [M] → [] → [M,M,M] → [M,M] → [M] → []
            Output: [Sesi1, Sesi2, Sesi3]
        """
        stack_masuk = []
        sesi_list = []
        
        for tap in tap_list:
            if tap.punch_type == 0:  # ✅ TAP MASUK
                # PUSH ke stack
                stack_masuk.append({
                    'tap_masuk': tap,
                    'tap_pulang': None,
                    'all_taps': [tap]
                })
            
            elif tap.punch_type == 1:  # ✅ TAP PULANG
                if stack_masuk:
                    # POP stack terakhir
                    sesi_data = stack_masuk.pop()
                    sesi_data['tap_pulang'] = tap
                    sesi_data['all_taps'].append(tap)
                    
                    # BUAT SESI dari data yang di-pop
                    sesi = cls._buat_sesi_data_v2(sesi_data)
                    sesi_list.append(sesi)
                else:
                    # Pulang tanpa masuk (skip)
                    print(f"⚠️ SKIP: Tap PULANG tanpa MASUK ({tap.waktu_tap})")
            
            elif tap.punch_type in [2, 3]:  # ⏭️ TAP ISTIRAHAT
                # Tambahkan ke sesi terakhir di stack (opsional)
                if stack_masuk:
                    stack_masuk[-1]['all_taps'].append(tap)
        
        # ⚠️ Handle sesi incomplete (masuk tapi belum pulang)
        for incomplete in stack_masuk:
            print(f"⚠️ Sesi INCOMPLETE: MASUK {incomplete['tap_masuk'].waktu_tap} (belum pulang)")
            # Bisa di-skip atau buat sesi incomplete
            sesi = cls._buat_sesi_data_v2(incomplete)
            sesi_list.append(sesi)
        
        return sesi_list
    
    @classmethod
    def _buat_sesi_data_v2(cls, sesi_data):
        """
        Buat data sesi dari dict yang di-pop dari stack
        
        Args:
            sesi_data: {
                'tap_masuk': TapLog,
                'tap_pulang': TapLog or None,
                'all_taps': [TapLog, ...]
            }
        
        Returns:
            dict: Sesi data untuk disimpan ke database
        """
        tap_masuk = sesi_data['tap_masuk']
        tap_pulang = sesi_data['tap_pulang']
        all_taps = sesi_data['all_taps']
        
        tanggal_masuk = tap_masuk.tanggal
        tanggal_pulang = tap_pulang.tanggal if tap_pulang else tanggal_masuk
        
        # Cek apakah lintas hari (shift malam)
        is_cross_day = tanggal_pulang > tanggal_masuk
        
        # Hitung durasi kerja
        if tap_pulang:
            dt_masuk = datetime.combine(tanggal_masuk, tap_masuk.waktu_tap)
            dt_pulang = datetime.combine(tanggal_pulang, tap_pulang.waktu_tap)
            durasi_menit = int((dt_pulang - dt_masuk).total_seconds() / 60)
        else:
            durasi_menit = 0
        
        # Kumpulkan semua tap_id dalam urutan
        tap_ids = [t.id for t in all_taps]
        
        # Hitung jumlah tap masuk & pulang
        jumlah_tap_masuk = sum(1 for t in all_taps if t.punch_type == 0)
        jumlah_tap_pulang = sum(1 for t in all_taps if t.punch_type == 1)
        
        return {
            'tanggal_mulai': tanggal_masuk,
            'tanggal_selesai': tanggal_pulang,
            'tap_masuk_pertama': tap_masuk.waktu_tap,
            'tap_masuk_terakhir': tap_masuk.waktu_tap,  # Untuk single masuk
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
        """
        Simpan sesi ke database dengan relasi tap
        
        Args:
            pegawai: Instance Pegawai
            sesi_data: dict dari _buat_sesi_data_v2
        """
        from .models import AbsensiSesi, TapSesiRelation, TapLog
        
        with transaction.atomic():
            # ========================================
            # 1. BUAT ABSENSI SESI
            # ========================================
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
            
            # ========================================
            # 2. BUAT RELASI DENGAN TAP LOGS
            # ========================================
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
            
            # ========================================
            # 3. MARK TAP SEBAGAI PROCESSED
            # ========================================
            TapLog.objects.filter(
                id__in=sesi_data['tap_ids']
            ).update(is_processed=True)
    
    @classmethod
    def get_sesi_summary_untuk_pegawai(cls, pegawai, tanggal_mulai, tanggal_akhir):
        """
        Ambil summary sesi untuk pegawai dalam range tanggal
        
        Args:
            pegawai: Instance Pegawai
            tanggal_mulai: date
            tanggal_akhir: date
            
        Returns:
            dict: {
                'sesi_list': QuerySet,
                'sesi_per_hari': dict,
                'total_sesi': int,
                'total_hari_kerja': int
            }
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