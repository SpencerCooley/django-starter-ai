
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema, OpenApiParameter
from core.celery import app as celery_app
from .serializers import (
    JobCreateRequestSerializer,
    JobCreateResponseSerializer,
    JobStatusResponseSerializer,
)

class JobView(APIView):
    @extend_schema(
        summary="Create and Dispatch a Celery Task",
        description="""
        This endpoint receives a job name and a payload, and dispatches it to a Celery worker.
        The `job_name` should be the full, importable path to the task function.
        The `payload` should be a JSON object containing the keyword arguments for the task.
        """,
        request=JobCreateRequestSerializer,
        responses={202: JobCreateResponseSerializer},
    )
    def post(self, request):
        serializer = JobCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        job_name = validated_data.get("job_name")
        payload = validated_data.get("payload", {})

        try:
            # Use kwargs to pass the payload as keyword arguments to the task
            task = celery_app.send_task(job_name, kwargs=payload)
            response_serializer = JobCreateResponseSerializer(data={"task_id": task.id})
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Check Celery Task Status",
        description="Retrieve the status and result of a Celery task using its unique ID.",
        parameters=[
            OpenApiParameter(
                name='job_id',
                description='The unique ID of the Celery task.',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            )
        ],
        responses={200: JobStatusResponseSerializer},
    )
    def get(self, request):
        task_id = request.query_params.get("job_id")
        if not task_id:
            return Response(
                {"error": "job_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = AsyncResult(task_id)
        
        # Gracefully handle non-JSON serializable results (like exceptions)
        task_result = result.result
        if isinstance(task_result, Exception):
            task_result = str(task_result)

        response_data = {
            "task_id": task_id,
            "status": result.status,
            "result": task_result,
        }
        
        serializer = JobStatusResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
