from rest_framework.views import APIView
from rest_framework.response import Response
from solar_api.services.solar_gen_prediction_service import SolarPredictionService

# Instantiate service at module level to load model once
prediction_service = SolarPredictionService()

class SolarGenerationPrediction(APIView):
    def get(self, request):
        pincode = request.GET.get("pincode")
        sunlight_time = request.GET.get("sunlight_time")
        panels = request.GET.get("panels")
        panel_condition = request.GET.get("panel_condition")

        result, status_code = prediction_service.predict_generation(
            pincode, sunlight_time, panels, panel_condition
        )

        return Response(result, status=status_code)
