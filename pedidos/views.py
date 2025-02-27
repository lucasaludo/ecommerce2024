from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView

from carrinho.carrinho import Carrinho
from pedidos.forms import PedidoModelForm
from pedidos.models import ItemPedido, Pedido


class PedidoCreateView(LoginRequiredMixin, CreateView):
    form_class = PedidoModelForm
    success_url = reverse_lazy('resumopedido')
    template_name = 'pedido/formpedido.html'

    def form_valid(self, form):
        car = Carrinho(self.request)
        pedido = form.save(commit=False)
        usuario = self.request.user
        pedido.cliente = usuario
        pedido.save()
        for item in car:
            ItemPedido.objects.create(pedido=pedido,
                                      produto=item['produto'],
                                      preco=item['preco'],
                                      quantidade=item['quantidade'])
        car.limpar()
        self.request.session['idpedido'] = pedido.id
        return redirect('resumopedido')


class ResumoPedidoTemplateView(TemplateView):
    template_name = 'pedido/resumopedido.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pedido'] = Pedido.objects.get(id=self.request.session.get('idpedido'))
        return ctx

class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedido/listar_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        return Pedido.objects.filter(cliente=self.request.user).order_by('-criado')
    
class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedido/detalhes_pedido.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        return Pedido.objects.filter(cliente=self.request.user)