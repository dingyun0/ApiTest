import requests

raw_text=[
"1.  Ever wondered how to keep your iPhone 15 Pro Max safe without hiding its beauty?",
"2.  Meet the ESR Classic Series case. It’s crystal clear to show off your phone’s original color, and it’s ultra-thin for a comfortable grip.",
"3.  Snap it on easily. Perfect fit every time. And yes, it’s fully compatible with MagSafe.",
"4.  Enjoy strong magnetic attachment for wireless charging and all your MagSafe accessories. It just clicks into place.",
"5.  With military-grade protection and raised edges, your screen and camera are well guarded. Keep it stylish, keep it protected.",

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
    response=requests.post(url,json=payload,verify=False)
    response.raise_for_status()
    response_json=response.json()
    duration=response_json["data"]["duration_s"]
    spliced_text=f"{raw_text[i]}（{duration}s）"
    result.append(spliced_text)

print("\n".join(result))