import json

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HistoryLog
from .permissions import IsAdminUser


class HistoryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):

        data = [
            (
                obj.id,
                obj.type,
                obj.change_message,
                str(obj.user),
                str(obj.client),
                str(obj.salesman),
                obj.action_time.strftime("%d-%m-%Y %H:%M"),
                json.dumps(obj.additional_info, ensure_ascii=False) if obj.additional_info else False,
            )
            for obj in HistoryLog.objects.all()[::-1]
            if obj.user
        ]

        json_data = json.dumps(data, ensure_ascii=False)

        return render(
            request,
            "data_template.html",
            {"data_json": json_data},
        )

    def delete(self, request, *args, **kwargs):
        HistoryLog.objects.all().delete()
        return Response(status=200)
