from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


# ==============================================================================
# FILTER - PEGAWAI
# Filter untuk data pegawai
# ==============================================================================

@register.filter
def get_pegawai_name(pegawai):
    """
    Ambil nama lengkap pegawai
    Fallback ke first_name + last_name atau username
    
    Usage: {{ pegawai|get_pegawai_name }}
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
# FILTER - DICTIONARY
# Filter untuk operasi dictionary di template
# ==============================================================================

@register.filter
def get_dict_item(dictionary, key):
    """
    Ambil value dari dictionary berdasarkan key
    Support integer dan string key
    
    Usage: {{ my_dict|get_dict_item:some_key }}
    """
    if dictionary is None:
        return None
    
    if not isinstance(dictionary, dict):
        return None
    
    try:
        # Convert key to string untuk consistency
        key_str = str(key)
        
        # Try to get with string key first
        if key_str in dictionary:
            return dictionary.get(key_str)
        
        # Try to get with integer key
        try:
            key_int = int(key)
            if key_int in dictionary:
                return dictionary.get(key_int)
        except (ValueError, TypeError):
            pass
        
        # Return None if not found
        return None
    except Exception:
        return None


@register.filter
def get_item(dictionary, key):
    """
    Alias untuk get_dict_item - untuk backward compatibility
    Ambil value dari dictionary berdasarkan key
    
    Usage: {{ my_dict|get_item:some_key }}
    """
    return get_dict_item(dictionary, key)


@register.filter
def dict_keys(dictionary):
    """
    Ambil semua keys dari dictionary sebagai list
    
    Usage: {{ my_dict|dict_keys }}
    """
    if isinstance(dictionary, dict):
        return list(dictionary.keys())
    return []


@register.filter
def dict_values(dictionary):
    """
    Ambil semua values dari dictionary sebagai list
    
    Usage: {{ my_dict|dict_values }}
    """
    if isinstance(dictionary, dict):
        return list(dictionary.values())
    return []


@register.filter
def dict_lookup(dictionary, key):
    """
    Lookup dictionary dengan key (alias untuk get_dict_item)
    
    Usage: {{ my_dict|dict_lookup:key_variable }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


# ==============================================================================
# FILTER - JADWAL
# Filter untuk operasi jadwal
# ==============================================================================

@register.filter
def jadwal_display(jadwal_id):
    """
    Display jadwal dengan format: jam_masuk - jam_keluar
    Jika jadwal_id kosong, tampilkan "🏠 LIBUR"
    
    Usage: {{ jadwal_id|jadwal_display }}
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
    Display jadwal dengan format lengkap: group_name (jam_masuk-jam_keluar)
    Jika jadwal_id kosong, tampilkan "🏠 LIBUR"
    
    Usage: {{ jadwal_id|jadwal_full_display }}
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


# ==============================================================================
# FILTER - TIME & DATE
# Filter untuk operasi waktu dan tanggal
# ==============================================================================

@register.filter
def format_time(time_obj, format_string="%H:%M"):
    """
    Format time object ke string
    
    Usage: {{ time_obj|format_time }}
    atau: {{ time_obj|format_time:"%H:%M:%S" }}
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
    atau: {{ date_obj|format_date:"%d/%m/%Y" }}
    """
    if not date_obj:
        return "-"
    
    try:
        return date_obj.strftime(format_string)
    except Exception:
        return str(date_obj)


# ==============================================================================
# FILTER - UTILITY
# Filter utility umum
# ==============================================================================

@register.filter
def add_space(value, spaces=1):
    """
    Tambah spasi sebelum value
    
    Usage: {{ value|add_space }}
    atau: {{ value|add_space:3 }}
    """
    try:
        space_count = int(spaces)
        return "&nbsp;" * space_count + str(value)
    except (ValueError, TypeError):
        return str(value)


@register.filter
def replace_newline(value):
    """
    Ganti newline dengan <br> (plain text, tidak aman untuk HTML injection)
    
    Usage: {{ value|replace_newline }}
    """
    if not value:
        return ""
    
    return str(value).replace('\n', '<br>')


@register.filter(is_safe=True)
def replace_newline_safe(value):
    """
    Ganti newline dengan <br> dengan escape HTML terlebih dahulu
    Lebih aman untuk menampilkan user input
    
    Usage: {{ value|replace_newline_safe|safe }}
    """
    if not value:
        return ""
    
    # Escape HTML entities terlebih dahulu
    escaped = escape(str(value))
    # Kemudian ganti newline dengan <br>
    return mark_safe(escaped.replace('\n', '<br>'))


@register.filter
def truncate_words(value, num_words=10):
    """
    Potong text setelah N kata
    
    Usage: {{ text|truncate_words:5 }}
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
    
    Usage: {{ text|truncate_chars:20 }}
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


@register.filter
def default_if_none(value, default_text="-"):
    """
    Tampilkan default text jika value None atau kosong
    
    Usage: {{ value|default_if_none }}
    atau: {{ value|default_if_none:"N/A" }}
    """
    if value is None or value == "":
        return default_text
    return value


@register.filter
def yes_no_icon(value):
    """
    Convert boolean ke icon (✓/✗)
    
    Usage: {{ is_active|yes_no_icon }}
    """
    if value:
        return mark_safe('✓')
    return mark_safe('✗')


@register.filter
def yes_no_badge(value, yes_text="Ya", no_text="Tidak"):
    """
    Convert boolean ke badge HTML
    
    Usage: {{ is_active|yes_no_badge }}
    atau: {{ is_active|yes_no_badge:"Active:Inactive" }}
    """
    try:
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
def add_ordinal_suffix(value):
    """
    Tambah ordinal suffix (st, nd, rd, th) ke number
    Contoh: 1 → 1st, 2 → 2nd, 3 → 3rd, 4 → 4th
    
    Usage: {{ number|add_ordinal_suffix }}
    """
    try:
        num = int(value)
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
        return f"{num}{suffix}"
    except (ValueError, TypeError):
        return str(value)


# ==============================================================================
# FILTER - STRING
# Filter untuk manipulasi string
# ==============================================================================

@register.filter
def upper_first(value):
    """
    Capitalize first character
    
    Usage: {{ text|upper_first }}
    """
    if not value:
        return ""
    
    text = str(value)
    return text[0].upper() + text[1:] if text else ""


@register.filter
def lower_first(value):
    """
    Lowercase first character
    
    Usage: {{ text|lower_first }}
    """
    if not value:
        return ""
    
    text = str(value)
    return text[0].lower() + text[1:] if text else ""


@register.filter
def remove_spaces(value):
    """
    Hapus semua spasi dari string
    
    Usage: {{ text|remove_spaces }}
    """
    if not value:
        return ""
    
    return str(value).replace(" ", "")


@register.filter
def join_list(value, separator=", "):
    """
    Join list items dengan separator
    
    Usage: {{ list|join_list }}
    atau: {{ list|join_list:" | " }}
    """
    if not value:
        return ""
    
    try:
        return separator.join(str(item) for item in value)
    except Exception:
        return str(value)