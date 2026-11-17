from faster_whisper import WhisperModel

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe(video_path):
    model = _get_model()
    segments, _ = model.transcribe(video_path, word_timestamps=True, vad_filter=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"word": w.word, "start": w.start, "end": w.end})
    return words