from rest_framework import viewsets, permissions, mixins
from .models import ReportReason, Report
from .serializers import ReportReasonSerializer, ReportSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only admin can do writes, normal users can do read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ReportReasonViewSet(viewsets.ModelViewSet):
    """
    Admin-only or read-only for listing reason definitions.
    You can allow everyone to read reasons if you want them displayed in a UI.
    """
    queryset = ReportReason.objects.all().order_by('order')
    serializer_class = ReportReasonSerializer
    permission_classes = [IsAdminOrReadOnly]


class IsAdminOrOwnerCanCreate(permissions.BasePermission):
    """
    Example permission:
      - Anyone can create a new report (including unauth?),
      - Only admin can list or update existing reports,
      - Or you can decide to let the reporting user see their own reports.
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return True  # allow creation by any user or even anonymous
        # For other actions, must be admin
        return request.user and request.user.is_staff


class ReportViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for reports. Typically:
      - create => open to all
      - list, retrieve, update => staff only
    If you want a user to see their own reports, you'd customize the permission.
    """
    queryset = Report.objects.all().order_by('-opened_at')
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrOwnerCanCreate]

    def perform_create(self, serializer):
        """
        Called on POST creation. 
        The serializer already sets user if authenticated or uses anonymous_email.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        If an admin updates the report status from pending->rejected or satisfied,
        we finalize it in `ReportSerializer.update()`.
        """
        serializer.save()
