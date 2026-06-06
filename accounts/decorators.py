from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to restrict views to admin users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin_user:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('client_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def client_required(view_func):
    """Decorator to restrict views to client users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_client:
            messages.error(request, 'This page is for members only.')
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
