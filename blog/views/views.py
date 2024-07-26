import csv
import json
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, F
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from openpyxl.workbook import Workbook
from django.views import View
from blog.models import Product, Customer, Order
from blog.forms import CustomerModelForm, ProductListModelForm
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView


# Index view for displaying paginated list of products
def index(request):
    products = Product.objects.all()
    paginator = Paginator(products, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/index.html', context)


# Product List View with Aggregated Data
class ProductListTemplateView(TemplateView):
    template_name = 'blog/product/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        paginator = Paginator(products, 2)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Aggregation
        total_quantity = Order.objects.filter(product__in=products).aggregate(total_quantity=Sum('quantity'))
        average_price = products.aggregate(average_price=Avg('price'))

        context["page_obj"] = page_obj
        context["total_quantity"] = total_quantity['total_quantity']
        context["average_price"] = average_price['average_price']
        return context


# Product Detail View with Annotated Data
class ProductDetailTemplateView(TemplateView):
    template_name = 'blog/product/product-detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(slug=kwargs['slug'])
        context['product'] = product
        context['attributes'] = product.get_attributes()
        return context


# Product Add View
class ProductAddTemplateView(TemplateView):
    template_name = 'blog/product/add-product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductListModelForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ProductListModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
        return self.render_to_response(self.get_context_data(form=form))


# Product Update View
class ProductUpdateView(View):
    def get(self, request, slug):
        product = Product.objects.get(slug=slug)
        form = ProductListModelForm(instance=product)
        return render(request, 'blog/product/update-product.html', {'form': form})

    def post(self, request, slug):
        product = Product.objects.get(slug=slug)
        form = ProductListModelForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('index')
        return render(request, 'blog/product/update-product.html', {'form': form})


# Customer List View with Annotated Data
class CustomersListView(ListView):
    model = Customer
    template_name = 'blog/customer/customers.html'
    context_object_name = 'page_obj'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(email__icontains=search_query))

        # Annotation
        queryset = queryset.annotate(total_revenue=Sum(F('order__quantity') * F('order__product__price')))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aggregation
        total_customers = Customer.objects.count()
        total_revenue = Customer.objects.aggregate(total_revenue=Sum(F('order__quantity') * F('order__product__price')))

        context['total_customers'] = total_customers
        context['total_revenue'] = total_revenue['total_revenue']
        return context


# Customer Add View
class CustomersAddListView(FormMixin, ListView):
    model = Customer
    template_name = 'blog/customer/add-customer.html'
    context_object_name = 'customers'
    form_class = CustomerModelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return redirect('customers')
        return self.render_to_response(self.get_context_data(form=form))


# Customer Detail View with Annotated Data
class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'blog/customer/customer-details.html'
    context_object_name = 'customer'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Customer, id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()

        # Annotation
        customer_total_revenue = Order.objects.filter(customer=customer).aggregate(total_revenue=Sum(F('quantity') * F('product__price')))

        context['total_revenue'] = customer_total_revenue['total_revenue']
        return context


# Customer Delete View
class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy('customers')

    def get(self, request, *args, **kwargs):
        return self.delete(self.request, *args, **kwargs)


# Customer Update View
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerModelForm
    template_name = 'blog/customer/update-customer.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return Customer.objects.get(id=pk)

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse_lazy('customers_detail', kwargs={'pk': pk})


# Export Data View with Aggregated Data
class ExportDataView(View):
    def get(self, request):
        format = request.GET.get('format', 'csv')

        if format == 'csv':
            response = self.export_csv()
        elif format == 'json':
            response = self.export_json()
        elif format == 'xlsx':
            response = self.export_xlsx()
        else:
            response = HttpResponse(status=404)
            response.content = 'Bad requests'

        return response

    def export_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'email', 'phone', 'billing_address', 'total_revenue'])

        customers = Customer.objects.annotate(total_revenue=Sum(F('order__quantity') * F('order__product__price')))
        for customer in customers:
            writer.writerow([customer.id, customer.name, customer.email, customer.phone, customer.billing_address, customer.total_revenue])
        return response

    def export_json(self):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="customers.json"'
        data = list(Customer.objects.annotate(total_revenue=Sum(F('order__quantity') * F('order__product__price')))
                    .values('id', 'name', 'email', 'phone', 'billing_address', 'total_revenue'))
        response.content = json.dumps(data, indent=4)
        return response

    def export_xlsx(self):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="customers.xlsx"'
        wb = Workbook()
        ws = wb.active
        ws.title = "Customers"

        headers = ["id", "name", "email", "phone", "billing_address", "total_revenue"]
        ws.append(headers)

        customers = Customer.objects.annotate(total_revenue=Sum(F('order__quantity') * F('order__product__price')))
        for customer in customers:
            ws.append([customer.id, customer.name, customer.email, customer.phone, customer.billing_address, customer.total_revenue])

        wb.save(response)
        return response
