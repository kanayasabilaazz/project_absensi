from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ==============================================================================
# FILTER - PEGAWAI
# ==============================================================================

@register.filter
def get_pegawai_name(pegawai):
    """
    Ambil nama lengkap pegawai dengan fallback
    Usage: {{ pegawai|get_pegawai_name }}
    Returns: nama_lengkap atau "First Last" atau username atau "Unknown"
    """
    if not pegawai:
        return "Unknown"
    
    if hasattr(pegawai, 'nama_lengkap') and pegawai.nama_lengkap:
        return pegawai.nama_lengkap
    
    if hasattr(pegawai, 'user'):
        full_name = f"{pegawai.user.first_name} {pegawai.user.last_name}".strip()
        return full_name or pegawai.user.username
    
    return "Unknown"


# ==============================================================================
# FILTER - DICTIONARY OPERATIONS
# ==============================================================================

@register.filter
def get_dict_item(dictionary, key):
    """
    Ambil value dari dictionary berdasarkan key (support string & integer key)
    Usage: {{ my_dict|get_dict_item:some_key }}
    Returns: value atau None jika key tidak ditemukan
    """
    if dictionary is None or not isinstance(dictionary, dict):
        return None
    
    try:
        key_str = str(key)
        
        if key_str in dictionary:
            return dictionary.get(key_str)
        
        try:
            key_int = int(key)
            if key_int in dictionary:
                return dictionary.get(key_int)
        except (ValueError, TypeError):
            pass
        
        return None
    except Exception:
        return None


@register.filter
def get_item(dictionary, key):
    """
    Alias untuk get_dict_item (backward compatibility)
    Usage: {{ my_dict|get_item:some_key }}
    ️Returns: value atau None jika key tidak ditemukan
    """
    return get_dict_item(dictionary, key)


# ==============================================================================
# FILTER - JADWAL & SCHEDULE
# ==============================================================================

@register.filter
def jadwal_display(jadwal_id):
    """
    Display jadwal: jam_masuk - jam_keluar
    """
    if not jadwal_id:
        return "🏠 LIBUR"
    
    try:
        from absensi_app.models import ModeJamKerjaJadwal
        jadwal = ModeJamKerjaJadwal.objects.get(id=jadwal_id)
        
        jam_masuk = jadwal.jam_masuk.strftime('%H:%M') if jadwal.jam_masuk else '-'
        jam_keluar = jadwal.jam_keluar.strftime('%H:%M') if jadwal.jam_keluar else '-'
        
        return f"{jam_masuk} - {jam_keluar}"
    except Exception:
        return "❌ Invalid"


@register.filter
def jadwal_full_display(jadwal_id):
    """
    Display jadwal lengkap: group_name (jam_masuk-jam_keluar)
    """
    if not jadwal_id:
        return "🏠 LIBUR"
    
    try:
        from absensi_app.models import ModeJamKerjaJadwal
        jadwal = ModeJamKerjaJadwal.objects.get(id=jadwal_id)
        
        jam_masuk = jadwal.jam_masuk.strftime('%H:%M') if jadwal.jam_masuk else '-'
        jam_keluar = jadwal.jam_keluar.strftime('%H:%M') if jadwal.jam_keluar else '-'
        
        return f"{jadwal.group_name} ({jam_masuk}-{jam_keluar})"
    except Exception:
        return "❌ Invalid"


@register.filter
def has_schedule(jadwal_obj):
    """
    Cek apakah jadwal valid (punya jam masuk & keluar)
    Usage: {{ jadwal_obj|has_schedule }}    
    """
    if not jadwal_obj:
        return False
    
    try:
        return (
            hasattr(jadwal_obj, 'jam_masuk') and jadwal_obj.jam_masuk and
            hasattr(jadwal_obj, 'jam_keluar') and jadwal_obj.jam_keluar
        )
    except Exception:
        return False


@register.filter
def get_day_name(hari_index):
    """
    Convert hari index (0-6) ke nama hari
    Usage: {{ hari_index|get_day_name }}
    Returns: Nama hari atau "Unknown"
    """
    hari_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    try:
        index = int(hari_index)
        if 0 <= index <= 6:
            return hari_names[index]
        return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"


# ==============================================================================
# FILTER - TIME & DATE FORMATTING
# ==============================================================================

@register.filter
def format_time(time_obj, format_string="%H:%M"):
    """
    Format time object ke string
    Usage: {{ time_obj|format_time }}
    Custom: {{ time_obj|format_time:"%I:%M %p" }}
    """
    if not time_obj:
        return "-"
    
    try:
        return time_obj.strftime(format_string)
    except Exception:
        return str(time_obj)


@register.filter
def format_date(date_obj, format_string="%d %b %Y"):
    """
    Format date object ke string
    Usage: {{ date_obj|format_date }}
    Custom: {{ date_obj|format_date:"%Y-%m-%d" }}
    """
    if not date_obj:
        return "-"
    
    try:
        return date_obj.strftime(format_string)
    except Exception:
        return str(date_obj)


# ==============================================================================
# FILTER - UTILITY
# ==============================================================================

@register.filter
def default_if_none(value, default_text="-"):
    """
    Tampilkan default text jika value None atau kosong
    Usage: {{ value|default_if_none:"N/A" }}
    ️Returns: value atau default_text
    """
    if value is None or value == "":
        return default_text
    return value


@register.filter
def yes_no_icon(value):
    """
    Convert boolean ke icon (✓/✗)
    Usage: {{ is_active|yes_no_icon }}
    ️Returns: '✓' jika True, '✗' jika False
    """
    if value:
        return mark_safe('✓')
    return mark_safe('✗')


@register.filter
def yes_no_badge(value, yes_text="Ya"):
    """
    Convert boolean ke badge HTML
    Usage: {{ is_active|yes_no_badge:"Yes:No" }}
    ️Returns: badge dengan teks sesuai nilai boolean
    """
    try:
        no_text = "Tidak"
        
        if ":" in str(yes_text):
            parts = str(yes_text).split(":")
            yes_text = parts[0]
            no_text = parts[1] if len(parts) > 1 else "Tidak"
        
        if value:
            badge = f'<span class="badge badge-success">{yes_text}</span>'
        else:
            badge = f'<span class="badge badge-danger">{no_text}</span>'
        
        return mark_safe(badge)
    except Exception:
        return str(value)


@register.filter
def truncate_words(value, num_words=10):
    """
    Potong text setelah N kata
    Usage: {{ text|truncate_words:20 }}
    ️Returns: truncated text dengan "..." jika lebih dari N kata
    """
    if not value:
        return ""
    
    try:
        words = str(value).split()
        truncated = ' '.join(words[:int(num_words)])
        if len(words) > int(num_words):
            truncated += '...'
        return truncated
    except Exception:
        return str(value)


@register.filter
def truncate_chars(value, num_chars=50):
    """
    Potong text setelah N karakter
    Usage: {{ text|truncate_chars:100 }}
    ️Returns: truncated text dengan "..." jika lebih dari N karakter
    """
    if not value:
        return ""
    
    try:
        text = str(value)
        num = int(num_chars)
        if len(text) > num:
            return text[:num] + '...'
        return text
    except Exception:
        return str(value)


# ==============================================================================
# FILTER - STRING MANIPULATION
# ==============================================================================

@register.filter
def upper_first(value):
    """
    Capitalize first character
    Usage: {{ text|upper_first }}
    ️Returns: Text dengan karakter pertama kapitalized
    """
    if not value:
        return ""
    
    text = str(value)
    return text[0].upper() + text[1:] if text else ""


@register.filter
def remove_spaces(value):
    """
    Hapus semua spasi dari string
    Usage: {{ text|remove_spaces }}
    ️Returns: Text tanpa spasi
    """
    if not value:
        return ""
    
    return str(value).replace(" ", "")


@register.filter
def join_list(value, separator=", "):
    """
    Join list items dengan separator
    Usage: {{ my_list|join_list:", " }}
    ️Returns: String gabungan dari list items
    """
    if not value:
        return ""
    
    try:
        return separator.join(str(item) for item in value)
    except Exception:
        return str(value)


# ==============================================================================
# FILTER - STATUS & BADGES
# ==============================================================================

@register.filter
def status_badge(status):
    """
    Convert status string ke badge dengan warna sesuai
    Usage: {{ status|status_badge }}
    ️Returns: badge HTML dengan warna sesuai status
    """
    status_colors = {
        'Hadir': 'success',
        'Sakit': 'warning',
        'Izin': 'info',
        'Absen': 'danger',
        'Incomplete': 'secondary',
    }
    
    color = status_colors.get(status, 'secondary')
    return mark_safe(f'<span class="badge badge-{color}">{status}</span>')


@register.filter
def active_badge(is_active):
    """
    Convert boolean active status ke badge
    Usage: {{ is_active|active_badge }}
    ️Returns: badge "Aktif" atau "Non-Aktif"
    """
    if is_active:
        return mark_safe('<span class="badge badge-success">Aktif</span>')
    return mark_safe('<span class="badge badge-secondary">Non-Aktif</span>')


# ==============================================================================
# FILTER - NUMERIC
# ==============================================================================

@register.filter
def format_duration(minutes):
    """
    Format menit ke format jam dan menit
    Usage: {{ total_minutes|format_duration }}
    ️Returns: "Xj Ym" atau "-" jika menit kosong
    """
    if not minutes:
        return "-"
    
    try:
        minutes = int(minutes)
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0:
            return f"{hours}j {mins}m"
        return f"{mins}m"
    except Exception:
        return str(minutes)


@register.filter
def add_value(value, arg):
    """
    Tambah nilai dengan angka
    Usage: {{ number|add_value:10 }}
    ️Returns: penjumlahan value dan arg
    """
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def subtract(value, arg):
    """
    Kurangi nilai dengan angka
    Usage: {{ number|subtract:5 }}
    ️Returns: pengurangan value dan arg
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value
    
@register.filter
def get_tap_status_class(absensi, tap_type='masuk'):
    """
    ✅ FIXED: Tentukan class CSS berdasarkan mode aktif pada tanggal absensi
    
    Usage: 
        {{ absensi|get_tap_status_class:'masuk' }}
        {{ absensi|get_tap_status_class:'pulang' }}
    
    Returns:
        'text-danger' jika terlambat/pulang cepat
        'text-success' jika normal
    """
    if tap_type == 'masuk':
        if absensi.is_late:
            return 'text-danger fw-bold'
        return 'text-success'
    
    elif tap_type == 'pulang':
        if absensi.is_early_departure:
            return 'text-danger fw-bold'
        return 'text-success'
    
    return ''


@register.filter
def get_mode_info_for_date(pegawai, tanggal):
    """
    ✅ NEW: Ambil info mode yang aktif pada tanggal tertentu
    
    Usage: {{ pegawai|get_mode_info_for_date:absensi.tanggal }}
    
    Returns:
        dict: {mode_nama, mode_warna, periode_nama, is_mode_khusus}
    """
    from absensi_app.services import LayananModeKerja
    
    mode_info = LayananModeKerja.ambil_mode_aktif(tanggal)
    
    if not mode_info or not mode_info['mode']:
        return {
            'mode_nama': 'Normal',
            'mode_warna': '#3B82F6',
            'periode_nama': None,
            'is_mode_khusus': False
        }
    
    mode = mode_info['mode']
    periode = mode_info['periode']
    
    return {
        'mode_nama': mode.nama,
        'mode_warna': mode.warna,
        'periode_nama': periode.nama if periode else None,
        'is_mode_khusus': periode is not None
    }