import os
import tempfile

import streamlit as st

from utils.downloader import download_video
from utils.transcriber import transcribe
from utils.titler import generate_title
from utils.clipper import make_clip

st.set_page_config(page_title="AI Clipper", layout="wide")
st.title("🎬 AI Clipper")
st.caption("Drop a link or file → get auto-clipped, subtitled, titled shorts.")

with st.sidebar:
    st.header("Settings")
    n_clips = st.slider("Number of clips", 1, 10, 3)
    clip_len = st.slider("Clip length (s)", 5, 90, 30)
    style = st.selectbox("Subtitle style", ["pop", "karaoke", "bounce", "plain"])
    transition = st.selectbox("Transition", ["none", "fade", "slideleft", "wipeup"])
    do_title = st.checkbox("AI-generate titles", value=True)

mode = st.radio("Input", ["URL", "Upload"], horizontal=True)

if mode == "URL":
    src = st.text_input("Video URL")
else:
    src = st.file_uploader("Video file", type=["mp4", "mov", "mkv", "webm"])

if st.button("🚀 Generate clips", type="primary"):
    if not src:
        st.error("Provide a URL or upload a file.")
        st.stop()

    with st.spinner("Fetching video..."):
        if mode == "URL":
            vpath = download_video(src)
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp.write(src.read())
            tmp.close()
            vpath = tmp.name

    with st.spinner("Transcribing (word-level)..."):
        words = transcribe(vpath)
    st.success(f"Transcribed {len(words)} words.")

    duration = int(words[-1]["end"]) if words else clip_len * n_clips
    step = max(clip_len, duration // n_clips)

    for i in range(n_clips):
        start = i * step
        end = min(start + clip_len, duration)
        if end - start < 3:
            break

        with st.spinner(f"Rendering clip {i + 1}/{n_clips}..."):
            out = make_clip(vpath, words, start, end, style, transition)
            title = (
                generate_title(vpath, start, end, words)
                if do_title
                else f"Clip {i + 1}"
            )

        st.subheader(f"{i + 1}. {title}")
        st.video(out)

        with open(out, "rb") as f:
            st.download_button(
                f"⬇ Download clip {i + 1}",
                f.read(),
                file_name=os.path.basename(out),
                key=f"dl{i}",
            )