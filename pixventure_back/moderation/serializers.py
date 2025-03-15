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
    # Renamed field to match the frontend payload:
    rejection_reason = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError("At least one rejection reason is required for rejection.")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context['request']
            moderator = request.user

            entity_type = validated_data['entity_type']
            entity_id = validated_data['entity_id']
            action = validated_data['action']
            comment = validated_data.get('comment', "")

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
                new_status = 2
                reasons = []
            else:
                new_status = 4  # REJECTED
                reason_ids = validated_data.get('rejection_reason', [])
                reasons = list(RejectionReason.objects.filter(id__in=reason_ids, is_active=True))
                if len(reasons) != len(reason_ids):
                    raise ValidationError("One or more rejection reasons are invalid or inactive.")

            entity.status = new_status
            entity.save()

            mod_action = ModerationAction.objects.create(
                post=entity if entity_type == 'post' else None,
                media_item=entity if entity_type == 'media' else None,
                old_status=old_status,
                new_status=new_status,
                owner=entity.owner,
                moderator=moderator,
                comment=comment,
            )
            if reasons:
                mod_action.rejection_reasons.add(*reasons)

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


        
class RejectionReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectionReason
        fields = ['id', 'name', 'description', 'order']