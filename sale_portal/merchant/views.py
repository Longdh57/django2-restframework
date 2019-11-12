from django.http import JsonResponse
from django.template.response import TemplateResponse


def index(request):
    return TemplateResponse(request, 'merchant/index.html')


def show(request, pk):
    # Trả về view, ví dụ TemplateResponse(request, 'merchant/show.html')
    pass


def detail(request, pk):
    # API detail
    return JsonResponse({
        'data': 'Hello Binh',
        'pk': pk
    }, status=200)


def create(request):
    # Trả về view tạo mới, ví dụ TemplateResponse(request, 'merchant/create.html')
    pass


def store(request):
    # API tạo mới
    pass


def edit(request, pk):
    # Trả về view edit, ví dụ TemplateResponse(request, 'merchant/edit.html')
    pass


def update(request, pk):
    # API cập nhật
    pass


def delete(request, pk):
    # API xóa
    pass
