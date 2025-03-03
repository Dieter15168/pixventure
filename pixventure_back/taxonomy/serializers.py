# taxonomy/serializers.py

from rest_framework import serializers
from .models import Term

class TermSerializer(serializers.ModelSerializer):
    """
    Handles both tag and category creation.
    The client must specify 'term_type' (1=Tag, 2=Category).
    """
    class Meta:
        model = Term
        fields = ['id', 'term_type', 'name', 'slug']
        extra_kwargs = {
            'slug': {'required': True},
            'term_type': {'required': True},
        }

    def validate(self, data):
        """
        Optional: custom validation, e.g. ensure no collision in slug
        with the same term_type.
        """
        return data
