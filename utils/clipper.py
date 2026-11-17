import os
import subprocess
import tempfile


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,20,20,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _ass(words, start, end, style):
    lines = [ASS_HEADER]
    for w in words:
        if w["end"] < start or w["start"] > end:
            continue
        s = max(w["start"], start) - start
        e = min(w["end"], end) - start
        txt = w["word"].strip().replace("{", "(").replace("}", ")")
        if not txt:
            continue

        if style == "pop":
            effect = r"{\fscx60\fscy60\t(0,120,\fscx115\fscy115)\t(120,220,\fscx100\fscy100)}"
        elif style == "bounce":
            effect = r"{\move(540,1800,540,1700,0,150)\t(0,150,\fscx110\fscy110)\t(150,300,\fscx100\fscy100)}"
        elif style == "karaoke":
            effect = r"{\c&H00FFFF&}"
        else:
            effect = ""

        lines.append(f"Dialogue: 0,{_ts(s)},{_ts(e)},Default,,0,0,0,,{effect}{txt}")
    return "\n".join(lines)


def make_clip(video_path, words, start, end, style="pop", transition="none", out_dir="clips"):
    os.makedirs(out_dir, exist_ok=True)
    name = f"clip_{int(start)}_{int(end)}.mp4"
    out = os.path.join(out_dir, name)

    ass = tempfile.NamedTemporaryFile(delete=False, suffix=".ass", mode="w", encoding="utf-8")
    ass.write(_ass(words, start, end, style))
    ass.close()

    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"subtitles={ass.name}"
    )

    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", video_path,
        "-t", str(end - start),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        out,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out