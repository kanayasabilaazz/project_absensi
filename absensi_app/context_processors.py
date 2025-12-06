from .models import MasterCabang

def cabang_context(request):
    """
    Context processor untuk cabang aktif
    
    ✅ FIX FINAL:
    - TIDAK ADA default cabang otomatis
    - Cabang tersimpan per browser (via session)
    - Persisten setelah reload/logout/login/close browser
    - Session bertahan 30 hari
    """
    context = {
        'cabang_aktif': None,
        'cabang_list': [],
    }
    
    # Skip untuk static files dan admin
    if hasattr(request, 'path'):
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/admin/jsi18n/', '/__debug__/']
        if any(request.path.startswith(path) for path in skip_paths):
            return context
    
    # Skip untuk non-authenticated users
    try:
        if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
            return context
    except AttributeError:
        return context
    
    # Query cabang dengan error handling
    try:
        # Ambil semua cabang aktif
        cabang_queryset = MasterCabang.objects.filter(is_active=True).only('id', 'nama', 'kode')
        context['cabang_list'] = list(cabang_queryset.order_by('nama'))
        
        # ========================================
        # ✅ FIX: AMBIL CABANG DARI SESSION (TIDAK ADA DEFAULT)
        # ========================================
        cabang_aktif_id = None
        if hasattr(request, 'session') and isinstance(request.session, dict):
            cabang_aktif_id = request.session.get('cabang_aktif_id')
        
        # Jika ada cabang_id di session, load cabang tersebut
        if cabang_aktif_id:
            try:
                context['cabang_aktif'] = MasterCabang.objects.only('id', 'nama', 'kode').get(
                    id=cabang_aktif_id, 
                    is_active=True
                )
            except (MasterCabang.DoesNotExist, ValueError, TypeError):
                # Cabang tidak valid (mungkin sudah dihapus), hapus dari session
                try:
                    if hasattr(request.session, 'pop'):
                        request.session.pop('cabang_aktif_id', None)
                        request.session.pop('cabang_aktif_nama', None)
                        request.session.modified = True
                except (AttributeError, TypeError, KeyError):
                    pass
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in cabang_context: {str(e)}")
        return {'cabang_aktif': None, 'cabang_list': []}
    
    return context