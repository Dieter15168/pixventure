# moderation/serializers.py

from rest_framework import serializers
from posts.models import Post
from media.models import MediaItem
from media.serializers import UnpublishedMediaItemSerializer
from moderation.models import ModerationAction, RejectionReason
from django.core.exceptions import ValidationError
from django.db import transaction

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
    rejection_reason = serializers.IntegerField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required for rejection.")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context['request']
            moderator = request.user  # must be admin (enforced by permission)
            entity_type = validated_data['entity_type']
            entity_id = validated_data['entity_id']
            action = validated_data['action']
            comment = validated_data.get('comment', "")
            
            # Retrieve the entity based on type.
            if entity_type == 'post':
                try:
                    entity = Post.objects.get(id=entity_id)
                except Post.DoesNotExist:
                    raise ValidationError("Post not found.")
            else:
                try:
                    entity = MediaItem.objects.get(id=entity_id)
                except MediaItem.DoesNotExist:
                    raise ValidationError("Media item not found.")

            old_status = entity.status

            if action == 'approve':
                # For both posts and media, we'll set approved status as 2.
                new_status = 2  
                rejection_reason_obj = None
            else:
                new_status = 4  # REJECTED
                try:
                    rejection_reason_obj = RejectionReason.objects.get(
                        id=validated_data['rejection_reason'], is_active=True
                    )
                except RejectionReason.DoesNotExist:
                    raise ValidationError("Invalid or inactive rejection reason.")

            # Update the entity status.
            entity.status = new_status
            entity.save()

            # Create a ModerationAction record.
            mod_action = ModerationAction.objects.create(
                post=entity if entity_type == 'post' else None,
                media_item=entity if entity_type == 'media' else None,
                old_status=old_status,
                new_status=new_status,
                owner=entity.owner,
                moderator=moderator,
                rejection_reason=rejection_reason_obj,
                comment=comment,
            )
            return mod_action

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "entity": instance.post.id if instance.post else instance.media_item.id,
            "old_status": instance.old_status,
            "new_status": instance.new_status,
            "moderator": instance.moderator.username if instance.moderator else None,
            "performed_at": instance.performed_at,
        }