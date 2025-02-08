from django.db import transaction
from rest_framework import serializers
from ..models import Video, Article, Source, SectionItemInfo, Section, SectionItemType
from ...assessment.models import Assessment


from django.db import transaction

class VideoSerializer(serializers.ModelSerializer):
    source = serializers.URLField()

    class Meta:
        model = Video
        exclude = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create the Video, Source, and associated SectionItemInfo record within a transaction.
        """
        source_url = validated_data.pop('source')
        section = validated_data.pop('section')
        sequence = validated_data.pop('sequence')

        with transaction.atomic():
            # Create or fetch the Source object
            source, created = Source.objects.get_or_create(url=source_url)

            # Ensure the source is linked correctly to the Video
            validated_data['source'] = source

            # Create the Video instance
            video = super().create(validated_data)

            # Create the SectionItemInfo record
            SectionItemInfo.create_item(
                section=section,
                sequence=sequence,
                item_type=SectionItemType.VIDEO,
                item_instance=video,
            )

        return video


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['created_at', "updated_at"]

    def create(self, validated_data):
        """
        Create the Article and the associated SectionItemInfo record.
        """
        section = validated_data.pop('section')
        sequence = validated_data.pop('sequence')

        with transaction.atomic():
            article = super().create(validated_data)
            SectionItemInfo.create_item(
                section=section,
                sequence=sequence,
                item_type=SectionItemType.ARTICLE,
                item_instance=article,
            )
        return article
