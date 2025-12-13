import logging
from .models import MasterCabang

logger = logging.getLogger(__name__)


def cabang_context(request):
    """
    Context processor untuk menampilkan cabang aktif dan daftar cabang.
    
    Returns:
        dict: {
            'cabang_aktif': MasterCabang object atau None,
            'cabang_list': List of cabang dicts
        }
    """
    
    context = {
        'cabang_aktif': None,
        'cabang_list': [],
    }
    
    if not hasattr(request, 'path'):
        return context
    
    skip_paths = [
        '/static/', '/media/', '/favicon.ico', 
        '/admin/jsi18n/', '/__debug__/'
    ]
    if any(request.path.startswith(path) for path in skip_paths):
        return context
    
    try:
        if (not hasattr(request, 'user') or 
            not request.user.is_authenticated or 
            not (request.user.is_staff or request.user.is_superuser)):
            return context
    except (AttributeError, TypeError):
        return context
    
    try:
        cabang_queryset = MasterCabang.objects.filter(
            is_active=True
        ).values('id', 'nama', 'kode').order_by('nama')
        
        context['cabang_list'] = list(cabang_queryset)
        
    except Exception as e:
        logger.error(f"Error loading cabang_list: {str(e)}")
        return context
    
    try:
        if not hasattr(request, 'session'):
            return context
        
        if not hasattr(request.session, 'get'):
            return context
        
        cabang_aktif_id = request.session.get('cabang_aktif_id')
        
        if cabang_aktif_id:
            try:
                cabang_aktif_id = int(cabang_aktif_id)
                
                cabang_aktif = MasterCabang.objects.get(
                    id=cabang_aktif_id,
                    is_active=True
                )
                
                context['cabang_aktif'] = cabang_aktif
                
            except (MasterCabang.DoesNotExist, ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid cabang_aktif_id in session: {cabang_aktif_id} ({str(e)})"
                )
                
                try:
                    request.session.pop('cabang_aktif_id', None)
                    request.session.pop('cabang_aktif_nama', None)
                    request.session.modified = True
                    request.session.save()
                    
                    logger.info("Cleaned up invalid cabang session")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning session: {str(cleanup_error)}")
                
                context['cabang_aktif'] = None
    
    except Exception as e:
        logger.error(f"Error in cabang_context: {str(e)}")
        return {
            'cabang_aktif': None,
            'cabang_list': context.get('cabang_list', [])
        }
    
    return context