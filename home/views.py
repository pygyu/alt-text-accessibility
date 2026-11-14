from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from .models import Goods, UploadedFile
from .forms import GoodsForm, UploadedFileForm

import os
from alt_text import settings



def main(request):
    main_list = Goods.objects.all()
    return render(request, 'home/main.html', {'main_list' : main_list})

def detail(request, goods_id):
    goods = Goods.objects.get(pk=goods_id)
    return render(request, 'home/detail.html', {'goods': goods})

def upload(request):
    submitted = False
    goodsupload = None
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            file_path = request.FILES['file_path']
            submitted = True
            
            fileupload = UploadedFile(
                file_path=file_path
            )
            fileupload.save()

            gpt_result = image_analysis(fileupload.file_path.path)
            
            goodsupload= Goods(
                image=fileupload,
                alt_text=gpt_result,
                name=file_path.name
            )
            goodsupload.save()

            return render(request, 'home/review.html', {
                'form': form,
                'submitted': submitted,
                'file_path': fileupload.file_path.name,
                'gpt_result': gpt_result,
                'goodsupload':goodsupload
            })
    else:
        form = UploadedFileForm()
    return render(request, 'home/upload.html', {'form': form, 'submitted': submitted, 'goodsupload':goodsupload})




def review(request, goods_id):
    goods = Goods.objects.get(image__id=goods_id)

    if request.method == 'POST':
        goods.name = request.POST.get('name')
        goods.alt_text = request.POST.get('alt_text')
        goods.save()

    return redirect('home')


def image_analysis(file_path):

    import os
    import azure.ai.vision as sdk
    import json

    service_options = sdk.VisionServiceOptions(os.environ["VISION_ENDPOINT"],
                                            os.environ["VISION_KEY"])

    file = file_path
    print("file, ",file)
    subject = file_path.split('.')[0]
    with open(file, 'rb') as f:
        image_buffer = f.read()

    image_source_buffer = sdk.ImageSourceBuffer()
    image_source_buffer.image_writer.write(image_buffer)
    vision_source = sdk.VisionSource(image_source_buffer=image_source_buffer)

    analysis_options = sdk.ImageAnalysisOptions()

    analysis_options.features = (
        sdk.ImageAnalysisFeature.DENSE_CAPTIONS |
        sdk.ImageAnalysisFeature.TEXT
    )

    analysis_options.language = "en"

    analysis_options.gender_neutral_caption = True

    image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options) # API 호출

    result = image_analyzer.analyze()
    text_li = []
    caption_li = []
    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        if result.dense_captions is not None:
            print(" Dense Captions:")
            
            for caption in result.dense_captions:
                print("   '{}', {}, Confidence: {:.4f}".format(caption.content, caption.bounding_box, caption.confidence))
                caption_li.append(caption.content)

        if result.text is not None:
            print(" Text:")
            
            for line in result.text.lines:
                points_string = "{" + ", ".join([str(int(point)) for point in line.bounding_polygon]) + "}"
                print("   Line: '{}', Bounding polygon {}".format(line.content, points_string))
                text_li.append(line.content)

    else:

        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print(" Analysis failed.")
        print("   Error reason: {}".format(error_details.reason))
        print("   Error code: {}".format(error_details.error_code))
        print("   Error message: {}".format(error_details.message))

    text_ext =  ' '.join(text_li)
    dic = {'caption' : caption_li, 'ocr' : text_ext }
    import os
    from openai import AzureOpenAI
    client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

    completion = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # e.g. gpt-35-instant # model=os.environ["AZURE_OPENAI_DEPLOYMENT"],이렇게 해도 답변 나옴.
    messages=[
        {
            "role": "user",
            "content": str(dic) +
            """위 딕셔너리의 caption의 value값은 이미지의 그림을 설명하는 것이고,
                ocr의 value값은 OCR된 이미지에 나와있는 모든 텍스트야.이 둘을 전체적으로 종합해서 이미지를 요약해서 존댓말로 설명해줘.
                그리고, ocr의 value값에 상품 유형별로 주의해야할 사항이 있으면 자세하게 말해주고, OCR value값 전체를 사람이 이해하기 쉽게 설명해줘.
                전체 답변을 2~3문장내로 요약해서 말해줘
                단, 다음 조건은 반드시 지켜. 너의 대답에 ['OCR', '네', '알겠습니다', 'OCR 정보에 따르면', '대체텍스트'] 이 단어들과 내가 든 예시는 절대!!!!!!!!!!!!!!!!! 사용하지마.""",
        },
    ],
)
    return completion.choices[0].message.content
