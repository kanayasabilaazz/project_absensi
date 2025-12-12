from .models import MasterCabang

def cabang_context(request):
    """
    Context processor untuk menampilkan cabang aktif dan daftar cabang.
    - Cabang disimpan di session (persisten 30 hari)
    - Tidak ada default cabang
    - Skip paths: /static/, /media/, dll
    """
    context = {
        'cabang_aktif': None,
        'cabang_list': [],
    }
    
    if hasattr(request, 'path'):
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/admin/jsi18n/', '/__debug__/']
        if any(request.path.startswith(path) for path in skip_paths):
            return context
    
    try:
        if (not hasattr(request, 'user') or 
            not request.user.is_authenticated or 
            not request.user.is_staff):
            return context
    except AttributeError:
        return context
    
    try:
        cabang_queryset = MasterCabang.objects.filter(
            is_active=True
        ).only('id', 'nama', 'kode').order_by('nama')
        
        context['cabang_list'] = list(cabang_queryset)
        
        cabang_aktif_id = None
        if hasattr(request, 'session') and isinstance(request.session, dict):
            cabang_aktif_id = request.session.get('cabang_aktif_id')
        
        if cabang_aktif_id:
            try:
                context['cabang_aktif'] = MasterCabang.objects.get(
                    id=cabang_aktif_id, 
                    is_active=True
                )
            except (MasterCabang.DoesNotExist, ValueError, TypeError):
                try:
                    if hasattr(request.session, 'pop'):
                        request.session.pop('cabang_aktif_id', None)
                        request.session.pop('cabang_aktif_nama', None)
                        request.session.modified = True
                except (AttributeError, TypeError, KeyError):
                    pass
                
                context['cabang_aktif'] = None
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in cabang_context: {str(e)}")
        return {'cabang_aktif': None, 'cabang_list': []}
    
    return context