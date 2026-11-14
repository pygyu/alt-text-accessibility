import os
from django.shortcuts import render

# Create your views here.

# views.py


from django.shortcuts import render
from django.http import JsonResponse
from .models import ImageAnalysisResult
import requests

def analyze_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        # Azure AI API 호출을 위한 준비 작업
        api_key = os.environ["VISION_KEY"]
        endpoint = os.environ["VISION_ENDPOINT"]
        api_url = f'{endpoint}/vision/v3.0/analyze'
        headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': api_key}
        params = {'visualFeatures': 'Description'}  # 필요한 기능에 따라 조절

        # 이미지 파일을 Azure AI API에 전송
        with open(image.temporary_file_path(), 'rb') as image_file:
            response = requests.post(api_url, headers=headers, params=params, data=image_file.read())

        # API 응답 처리
        if response.status_code == 200:
            result_data = response.json()
            description = result_data.get('description', {}).get('captions', [{}])[0].get('text', '')

            # 결과를 모델에 저장
            result = ImageAnalysisResult.objects.create(
                image=image,
                description=description,
                azure_response=result_data
            )

            return JsonResponse({'status': 'success', 'result_id': result.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to analyze the image.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


from django.shortcuts import render
from .models import ImageAnalysisResult

def display_result(request, result_id):
    result = ImageAnalysisResult.objects.get(pk=result_id)
    return render(request, 'azure_image_analyzer/display_result.html', {'result': result})


#open api 부분

# views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings  # settings 모듈 추가
from .models import ImageAnalysisResult
import openai

def summarize_text(request, result_id):
    result = ImageAnalysisResult.objects.get(pk=result_id)
    input_text = result.description  # 이미지 분석 결과에서 얻은 텍스트

    # OpenAI GPT API 호출
    openai.api_key = settings.YOUR_OPENAI_API_KEY
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=input_text,
        temperature=0.7,
        max_tokens=150
    )

    # GPT API 응답 처리
    summary = response['choices'][0]['text']

    # 결과를 모델에 저장
    result.summary = summary
    result.save()

    return JsonResponse({'status': 'success', 'result_id': result.id, 'summary': summary})