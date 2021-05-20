from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Category
from .serializers import CategorySerializer


@api_view(['GET'])
def request_by_parent_view(request, parent_id):
    """
    :param request: HTTP request
    :param parent_id: Primary key of the parent node
    :return: JSON data containing all children of the parent node
    """
    if request.method == 'GET':
        try:
            category = Category.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            return HttpResponse("Parent Category doesn't exist.", status=status.HTTP_404_NOT_FOUND)

        if category.is_leaf_node():
            return HttpResponse("Category is a leaf node.", status=status.HTTP_403_FORBIDDEN)

        queryset = category.get_children()

        serializer = CategorySerializer(queryset, many=True)

        return Response(serializer.data)


@api_view(['GET'])
def request_by_level_view(request, level):
    """
        :param request: HTTP request
        :param level: Level of the category tree
        :return: JSON data containing all the category nodes on the given level
    """
    if request.method == 'GET':
        queryset = Category.objects.filter(level=level)
        if not queryset:
            return HttpResponse("No category nodes on level {}".format(level),
                                status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(queryset, many=True)

        return Response(serializer.data)


class CategoryAPIView(generics.ListAPIView):
    """
    View responsible for returning all categories or creating a new one.
    """

    def __init__(self, *args, **kwargs):
        self.serializer_class = CategorySerializer
        super().__init__(*args, **kwargs)

    def get(self, request):
        self.queryset = Category.objects.all()
        serializer = self.get_serializer(self.queryset, many=True)

        return Response(serializer.data)

    @csrf_exempt
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SingleCategoryAPIView(generics.GenericAPIView):
    """
    View handling GET/PUT/DELETE single category requests by pk
    url: categories/<int:id>
    """

    def __init__(self, *args, **kwargs):
        self.serializer_class = CategorySerializer
        super().__init__(*args, **kwargs)

    def get(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return HttpResponse("404 Category doesn't exists", status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(category)

        return Response(serializer.data)

    def put(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return HttpResponse("404 Category doesn't exists", status=status.HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)
        serializer = self.get_serializer(category, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return HttpResponse("404 Category doesn't exists", status=status.HTTP_404_NOT_FOUND)

        if category.parent is None:
            return HttpResponse("Cannot delete root node!", status=status.HTTP_403_FORBIDDEN)
        category.delete()

        return HttpResponse("Resource deleted successfully.", status=status.HTTP_204_NO_CONTENT)


def _get_categories(id1, id2):
    try:
        category_1 = Category.objects.get(id=id1)
    except ObjectDoesNotExist:
        category_1 = None

    try:
        category_2 = Category.objects.get(id=id2)
    except ObjectDoesNotExist:
        category_2 = None

    return category_1, category_2


class SimilarityCategoryView(generics.UpdateAPIView):
    """
        View handling POST/DELETE operations for Category objects similarities
        url: categories/<int:first_id>/similar/<int:second_id>
    """

    def __init__(self, *args, **kwargs):
        self.serializer_class = CategorySerializer
        super().__init__(*args, **kwargs)

    def post(self, request, first_id, second_id):
        category_1, category_2 = _get_categories(first_id, second_id)

        if not category_1:
            return HttpResponse("404 First category doesn't exists",
                                status=status.HTTP_404_NOT_FOUND)
        elif not category_2:
            return HttpResponse("404 Second category doesn't exists",
                                status=status.HTTP_404_NOT_FOUND)

        category_1.similar.add(category_2)
        category_1.save()
        category_1.refresh_from_db()

        serializer = self.get_serializer([category_1, category_2], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, first_id, second_id):
        category_1, category_2 = _get_categories(first_id, second_id)

        if not category_1:
            return HttpResponse("404 First category doesn't exists",
                                status=status.HTTP_404_NOT_FOUND)
        elif not category_2:
            return HttpResponse("404 Second category doesn't exists",
                                status=status.HTTP_404_NOT_FOUND)

        category_1.similar.remove(category_2)
        category_1.save()
        category_1.refresh_from_db()

        serializer = self.get_serializer([category_1, category_2], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
