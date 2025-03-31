# moderation/serializers.py

from rest_framework import serializers
from posts.models import Post
from media.serializers import UnpublishedMediaItemSerializer
from moderation.models import RejectionReason

class PostModerationSerializer(serializers.ModelSerializer):
    media_items = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'name', 'slug', 'status_display', 'created', 'updated', 'media_items']

    def get_media_items(self, obj):
        # Gather media items attached via PostMedia (assuming the related name is "post_media_links")
        media_objs = [link.media_item for link in obj.post_media_links.all()]
        serializer = UnpublishedMediaItemSerializer(media_objs, many=True, context=self.context)
        return serializer.data

    def get_status_display(self, obj):
        return obj.get_status_display()


class ModerationActionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a moderation action.
    Validates the input data and transforms it for processing.
    """
    ENTITY_TYPE_CHOICES = (
        ('post', 'Post'),
        ('media', 'MediaItem'),
    )
    ACTION_CHOICES = (
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    )
    entity_type = serializers.ChoiceField(choices=ENTITY_TYPE_CHOICES)
    entity_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    rejection_reason = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    comment = serializers.CharField(required=False, allow_blank=True)
    is_featured_post = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        """
        Ensure that when the action is a rejection, at least one rejection reason is provided.
        """
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError("At least one rejection reason is required for rejection.")
        return data

    def to_representation(self, instance):
        """
        Return the serialized representation of the moderation action.
        """
        return {
            "id": instance.id,
            "entity": instance.post.id if instance.post else instance.media_item.id,
            "old_status": instance.old_status,
            "new_status": instance.new_status,
            "moderator": instance.moderator.username if instance.moderator else None,
            "performed_at": instance.performed_at,
        }

        
class RejectionReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectionReason
        fields = ['id', 'name', 'description', 'order']