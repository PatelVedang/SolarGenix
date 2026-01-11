from rest_framework.views import APIView
from rest_framework.response import Response
from solar_api.services.bill_prediction_service import BillPredictionService

# Instantiate service at module level
bill_service = BillPredictionService()

class BillPredictionView(APIView):
    def get(self, request):
        # consumption_history is expected as a list of 6 values
        # e.g., ?consumption_history=100&consumption_history=150...
        consumption_history = request.GET.getlist("consumption_history")
        cycle_index = request.GET.get("cycle_index")

        result, status_code = bill_service.predict_bill(
            consumption_history, cycle_index
        )

        return Response(result, status=status_code)


