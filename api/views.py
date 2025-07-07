
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from core.celery import app as celery_app

class JobView(APIView):
    def post(self, request):
        job_name = request.data.get("job_name")
        payload = request.data.get("payload")

        if not job_name:
            return Response(
                {"error": "job_name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = celery_app.send_task(job_name, args=[payload])
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        task_id = request.query_params.get("job_id")
        if not task_id:
            return Response(
                {"error": "job_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = AsyncResult(task_id)
        response_data = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
        }
        return Response(response_data, status=status.HTTP_200_OK)
