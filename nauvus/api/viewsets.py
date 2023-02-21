# -*- coding: utf-8 -*-

from rest_framework import mixins, viewsets


class BaseGenericViewSet(viewsets.GenericViewSet):
    """Custom API response format."""


class BaseModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""


class BaseCreateViewSet(mixins.CreateModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseCreateListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseCreateRetrieveViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseCreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""


class BaseListViewSet(mixins.ListModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseListUpdateViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseRetrieveUpdateViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseRetrieveViewSet(mixins.RetrieveModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseUpdateViewSet(mixins.UpdateModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseCreateUpdateViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, BaseGenericViewSet):
    """Custom API response format."""


class BaseCreateListDeleteViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""


class BaseDeleteViewSet(
    mixins.DestroyModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""


class BaseCreateRetrieveDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""


class BaseCreateListUpdateViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    BaseGenericViewSet,
):
    """Custom API response format."""
