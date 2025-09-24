import requests

raw_text=[
    "1. Rich brown serums with white droppers, creamy eye creams in luxe jars—sleek, premium, and ready to glow.",
    "2. Bifida ferment melts in, hyaluronic acid hydrates deep, peptides and antioxidants work their magic: 7-night repair, visible science.",
    "3. Late-night work? Dab serum on tired skin. Baby’s asleep? Pat eye cream gently. Soft lights, real moments, simple self-care.",
    "4. 28 days: finer lines. 2 weeks: brighter under eyes. Nighttime repair, morning radiance—this duo’s your secret.",
]

newtext=[text.split('.',1)[1] if '.' in text else text for text in raw_text]
url="https://wisemaa.yingsaidata.com/video/text_to_voice"
voice_id="zeeTdrCqbhpVKOucLtOKdhytM7rbJx5t"
speed=1
result=[]

for i,text in enumerate(newtext):
    payload={
        "text":text,
        "voiceID":voice_id,
        "speed":speed
    }
    response=requests.post(url,json=payload)
    response.raise_for_status()
    response_json=response.json()
    duration=response_json["data"]["duration_s"]
    spliced_text=f"{raw_text[i]}（{duration}s）"
    result.append(spliced_text)

print("\n".join(result))