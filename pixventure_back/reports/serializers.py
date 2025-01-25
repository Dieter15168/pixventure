from rest_framework import serializers
from .models import Report, ReportReason

class ReportReasonSerializer(serializers.ModelSerializer):
    """
    Basic serializer for managing report reasons.
    """
    class Meta:
        model = ReportReason
        fields = ['id', 'name', 'description', 'order', 'is_active']

class ReportSerializer(serializers.ModelSerializer):
    """
    For creating/updating a Report object.
    - The user or anonymous_email can be set in create.
    - On update, a moderator can set status, moderator_comment, closed_at, etc.
    """
    status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'post',
            'media_item',
            'user',
            'anonymous_email',
            'reason',
            'user_comment',
            'moderator_comment',
            'status',
            'status_display',
            'opened_at',
            'closed_at',
            'moderation_action',
        ]
        read_only_fields = ['user', 'opened_at', 'closed_at', 'moderation_action']

    def get_status_display(self, obj):
        return obj.get_status_display()

    def create(self, validated_data):
        """
        When a user creates a new report:
          - user might be set from request.user if authenticated
          - if not authenticated, use anonymous_email
        """
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        # If user is set, store it, else rely on anonymous_email
        validated_data['user'] = user
        report = super().create(validated_data)
        return report

    def update(self, instance, validated_data):
        """
        If the admin is resolving, they can set status=REJECTED or SATISFIED,
        optionally also set moderator_comment, closed_at, etc.
        """
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        if old_status == Report.PENDING and new_status in [Report.REJECTED, Report.SATISFIED]:
            # Mark resolved
            instance.mark_resolved(new_status, validated_data.get('moderator_comment'))

            # Remove them from validated_data to avoid double assignment
            validated_data.pop('status', None)
            validated_data.pop('moderator_comment', None)
        # else, if still pending, or partial update, we handle normal fields
        return super().update(instance, validated_data)
