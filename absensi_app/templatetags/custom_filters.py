from django import template

register = template.Library()


# ==============================================================================
# FILTER - PEGAWAI
# Filter untuk data pegawai
# ==============================================================================

@register.filter
def get_Pegawai_name(Pegawai):
    """
    Ambil nama lengkap pegawai
    Fallback ke first_name + last_name atau username
    """
    if Pegawai.nama_lengkap:
        return Pegawai.nama_lengkap
    
    if hasattr(Pegawai, 'user'):
        full_name = f"{Pegawai.user.first_name} {Pegawai.user.last_name}".strip()
        return full_name or Pegawai.user.username
    
    return "Unknown"


# ==============================================================================
# FILTER - DICTIONARY
# Filter untuk operasi dictionary di template
# ==============================================================================

@register.filter
def get_item(dictionary, key):
    """
    Akses dictionary key di template
    Support integer dan string key
    
    Usage: {{ my_dict|get_item:key_variable }}
    """
    if dictionary is None:
        return None
    
    if not isinstance(dictionary, dict):
        return None
    
    # Handle integer keys
    if isinstance(key, int):
        return dictionary.get(key)
    
    # Handle string keys yang mungkin integer
    try:
        int_key = int(key)
        # Try int key first
        result = dictionary.get(int_key)
        if result is not None:
            return result
        # Fallback to string key
        return dictionary.get(str(int_key))
    except (ValueError, TypeError):
        pass
    
    # Handle pure string keys
    return dictionary.get(key)


@register.filter
def dict_lookup(dictionary, key):
    """
    Lookup dictionary dengan key
    
    Usage: {{ my_dict|dict_lookup:key_variable }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None