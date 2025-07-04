def usuario_context(request):
    user = None
    if request.session.get('usuario_id'):
        from .models import Usuario
        user = Usuario.objects.filter(id=request.session['usuario_id']).first()
    return {'user': user}