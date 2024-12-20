from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

class BaseView(View):
    template_name = None
    title = ""
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = {
            'welcome': self.title,
            **kwargs
        }
        return context
    
    def render(self, request, context=None):
        if context is None:
            context = {}
        return render(request, self.template_name, self.get_context_data(**context))
