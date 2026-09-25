from rest_framework import serializers


class ErrorDetailSerializer(serializers.Serializer):
    """DRF default error body for 403, 404 and 429 (tech.md, section 7)."""

    detail = serializers.CharField()
