from rest_framework import serializers
from engagement.models import Like, ReadLater


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model.
    Simple serializer for like/unlike functionality.

    The author is automatically set from request.user.profile
    in the view's perform_create method.
    """
    class Meta:
        model = Like
        fields = ['id', 'article', 'created']
        read_only_fields = ['id', 'created']


class ReadLaterSerializer(serializers.ModelSerializer):
    """
    Serializer for ReadLater (bookmarks) model.
    Includes nested article details for user's reading list.

    The author is automatically set from request.user.profile
    in the view's perform_create method.
    """
    article_detail = serializers.SerializerMethodField()

    class Meta:
        model = ReadLater
        fields = ['id', 'article', 'article_detail', 'created']
        read_only_fields = ['id', 'created']

    def get_article_detail(self, obj):
        """
        Return article summary for bookmarked items.
        Avoids circular import by importing inside method.
        """
        from content.serializers import ArticleListSerializer
        return ArticleListSerializer(obj.article, context=self.context).data
