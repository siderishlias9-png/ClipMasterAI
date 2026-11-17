import os
import base64
import cv2
import google.generativeai as genai


def _frames(video_path, start, end, n=3):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    out = []
    for i in range(n):
        t = start + (end - start) * (i + 0.5) / n
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
        ok, frame = cap.read()
        if not ok:
            continue
        _, buf = cv2.imencode(".jpg", frame)
        out.append(base64.b64encode(buf).decode())
    cap.release()
    return out


def generate_title(video_path, start, end, words):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Clip"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    transcript = " ".join(w["word"] for w in words if start <= w["start"] <= end)

    parts = [{
        "text": (
            "Generate a short, catchy title (max 8 words, no quotes) for this "
            f"video clip. Transcript: {transcript}"
        )
    }]
    for b64 in _frames(video_path, start, end):
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})

    try:
        resp = model.generate_content(parts)
        return resp.text.strip().split("\n")[0][:80]
    except Exception:
        return "Clip"