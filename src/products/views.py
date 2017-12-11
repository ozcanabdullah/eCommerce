from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Product


class ProductFeaturedListView(ListView):
    template_name = 'products/list.html'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()


class ProductFeaturedDetailView(DetailView):
    queryset = Product.objects.all().featured()
    template_name = 'products/featured-detail.html'

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Product.objects.featured()


class ProductListView(ListView):
    template_name = 'products/list.html'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)


class ProductDetailSlugView(DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404('Not found...')
        except Product.MultipleObjectsReturned:
            queryset = Product.objects.filter(slug=slug, active=True)
            instance = queryset.first()
        except:
            raise Http404('Uhhhmmm')
        return instance



class ProductDetailView(DetailView):
    # queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        # context['abc'] = 123
        return context

    # def get_object(self, *args, **kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     instance = Product.objects.get_by_id(pk)
    #     if instance is None:
    #         raise Http404('Products doesn`t exist')
    #
    #     return instance

    def get_queryset(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        return Product.objects.filter(pk=pk)


def product_detail_view(request, pk=None, *args, **kwargs):
    # instance = Product.objects.get(pk=pk)  # id
    # instance = get_object_or_404(Product, pk=pk)
    # try:
    #     instance = Product.objects.get(id=4)
    # except Product.DoesNotExist:
    #     print('no product here')
    #     raise Http404('Product doesn`t exist')
    # except:
    #     print('huh?')

    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404
    print(instance)
    #
    # qs = Product.objects.filter(id=pk)
    #
    # if qs.exists() and qs.count() == 1:  # len(qs)
    #     instance = qs.first()
    # else:
    #     raise Http404('Products doesn`t exist')

    context = {
        'object': instance
    }
    return render(request, 'products/detail.html', context)
