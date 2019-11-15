from rest_framework import serializers

from bitmex.models import Parameter, Threshold


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = "__all__"


class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = "__all__"
        # lookup_field = "timeframe"
        # extra_kwargs = {
        #     'url': {'lookup_field': 'timeframe'}
        # }