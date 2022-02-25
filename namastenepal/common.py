"""
functions for common usages
"""
import json
import sys
from io import BytesIO
from uuid import UUID

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Count
from django.shortcuts import _get_queryset
from rest_framework.exceptions import ValidationError


def compress_image(uploaded_image):
    """
    compresses image
    """

    image_temporary = Image.open(uploaded_image)
    image_temporary = image_temporary.convert("RGB")
    output_io_stream = BytesIO()
    image_temporary.resize((1020, 573))
    image_temporary.save(output_io_stream, format="JPEG", quality=60)
    output_io_stream.seek(0)

    return InMemoryUploadedFile(
        output_io_stream,
        "ImageField",
        f"{uploaded_image.name.split('.')[0]}.jpg",
        "image/jpeg",
        sys.getsizeof(output_io_stream),
        None,
    )


def get_object_or_404(error_message, klass, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    :param error_message: message to return if not found
    :param klass: Model class
    """

    queryset = _get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*filter_args, **filter_kwargs)
    except queryset.model.DoesNotExist:
        raise ValidationError(error_message, code=404)


def get_exact_match(model_class, m2m_field, ids):
    query = model_class.objects.annotate(count=Count(m2m_field)).filter(count=len(ids))
    for _id in ids:
        query = query.filter(**{m2m_field: _id})
    return query


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
