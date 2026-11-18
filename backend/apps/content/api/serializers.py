"""Response DTOs of tech.md, section 7. Names become openapi.yaml components."""

from rest_framework import serializers


class ImageAssetSerializer(serializers.Serializer):
    url = serializers.CharField()
    srcset = serializers.CharField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    alt = serializers.CharField()
    color = serializers.CharField()


class SocialLinkSerializer(serializers.Serializer):
    # DRF pops declared fields off the class; the stubs still see Field.label.
    label = serializers.CharField()  # type: ignore[assignment]
    url = serializers.CharField()


class SiteSettingsSerializer(serializers.Serializer):
    phone = serializers.CharField()
    phone_display = serializers.CharField()
    max_phone = serializers.CharField()
    max_phone_display = serializers.CharField()
    vk_url = serializers.CharField()
    email = serializers.CharField()
    address = serializers.CharField()
    work_hours = serializers.CharField()
    map_url = serializers.CharField()
    social_links = SocialLinkSerializer(many=True)


class CategorySummarySerializer(serializers.Serializer):
    slug = serializers.CharField()
    title = serializers.CharField()
    short_description = serializers.CharField()
    cover = ImageAssetSerializer(allow_null=True)


class GalleryItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.CharField()
    category_title = serializers.CharField()
    title = serializers.CharField()
    caption = serializers.CharField()
    image = ImageAssetSerializer()


class HomeSlotsSerializer(serializers.Serializer):
    hero = ImageAssetSerializer(allow_null=True)
    about = ImageAssetSerializer(allow_null=True)
    material_ldsp = ImageAssetSerializer(allow_null=True)
    material_mdf = ImageAssetSerializer(allow_null=True)


class HomeContentSerializer(serializers.Serializer):
    slots = HomeSlotsSerializer()
    categories = CategorySummarySerializer(many=True)
    featured = GalleryItemSerializer(many=True)


class CategoryDetailSerializer(CategorySummarySerializer):
    description = serializers.CharField()
    seo_title = serializers.CharField()
    seo_description = serializers.CharField()
    gallery = GalleryItemSerializer(many=True)
