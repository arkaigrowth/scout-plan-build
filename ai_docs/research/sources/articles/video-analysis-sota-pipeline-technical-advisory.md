# SOTA Video Analysis Pipeline Architecture (2025)

**Source**: Technical Advisory
**Topic**: video-analysis-sota-pipeline
**Author**: GPT 5.1 (chad)
**Date Analyzed**: 2025-11-23
**Analyzed By**: Claude

---

Reality check: if you let one VLM do everything (keyframes + classification + extraction + narration), you're basically begging for verbose fan-fic. SOTA pipelines in 2025 are modular + coarse-to-fine, even when they use VLMs.

Here's a steelmanned, agile, low-friction architecture you can ship now and extend later.

⸻

## North-star principles (robust + low drama)

1. **Coarse → fine**. First find candidate frames/artifacts, then read them. Adaptive keyframe sampling papers keep hammering this because uniform sampling misses fast charts/slides.
2. **Specialists beat generalists for extraction**. Charts/tables/slide text are best handled by dedicated models (DePlot; Table Transformer/TABLET) then LLM reasoning.
3. **Ground or verify any VLM output**. Pixel/region grounding (VideoGLaMM-style) or a second verification pass reduces hallucinations a lot.
4. **Make every stage swappable**. You want YOLO today, open-vocab detection tomorrow, some new VLM next month.

⸻

## High-level pipeline (modules + contracts)

### 0) Ingest & normalize
- **Input**: YouTube URL(s)
- **Do**: download (yt-dlp), normalize FPS/resolution, extract audio + transcript (Whisper/Gemini/YouTube).
- **Output contract**: video.mp4, audio.wav, transcript.json (time-aligned).

### 1) Temporal segmentation (cheap and reliable)

Goal: split long videos into coherent units so you don't sample blindly.

- **Option A (lowest friction)**: PySceneDetect ContentDetector. CPU-friendly, simple API.
- **Option B (more accurate)**: TransNetV2 shot boundary NN. Still easy to run infer-only.
- **Option C (lecture/slide videos)**: slide-transition detectors (SliTraNet or YOLO-screen). Better for "talk + slides" where shots are long.

Output: list of segments {t_start, t_end, segment_type_guess}.

### 2) Candidate keyframe generation (coarse sampling)

Within each segment:
- grab 1–3 representative frames (middle + max-difference)
- plus burst sampling around transitions (±1–2s) to catch "flash graphs".

Adaptive methods like AKS / TriPSS / LMSKE show this consistently outperforms naive N-frames-per-minute.

Output: candidate_frames[] with timestamps.

### 3) Dedup + quality filter
- perceptual hash / SSIM clustering
- drop blurry frames, near-duplicates, "talking head only" if your task is slides.

Keyframe pipelines routinely add this to keep downstream compute sane.

Output: keyframes[] (clean list).

### 4) Visual artifact classification (light pass)

This is where you stop Gemma from going wild.
Task: label each keyframe with:
{slide, chart/plot, table, diagram, code, normal scene, other}

Top options:
- **Option A: small VLM "classifier-only" prompt**.
  - Pros: simplest, no training, runs local.
  - Cons: can still drift if prompt sloppy.
- **Option B: open-vocabulary detector on keyframes (GroundingDINO / OWLv2 / similar) + rules**.
  - Pros: more literal than captions; easy "find charts/tables/screens".
  - Cons: extra dependency.
  - Open-vocab + keyframe-only invocation is SOTA for efficiency.
- **Option C: YOLO tuned for screens/slides**.
  - Pros: very fast; great if your domain is mostly presentations.
  - Cons: needs labeled finetune if you want high recall.

Output: artifact_frames[] grouped by type.

### 5) Deep extraction (specialists first)

Run only on artifact_frames:
- **Charts/plots → DePlot → structured table → LLM summary**.
  This is the cleanest way to avoid numeric hallucination.
- **Tables → Table Transformer / TABLET / TableStructureFormer → HTML/CSV**.
  Table Transformer is the most plug-and-play OSS baseline; TABLET/others can be swapped later if you need denser tables.
- **Text slides/diagrams → OCR or doc-VLM (Pix2Struct/Donut-style) → cleaned text**.
  Qwen2.5-VL and InternVL2.5 are strong local doc/OCR models if you want to stay VLM-centric.

Output: per-artifact structured payloads.

### 6) Gap detection vs transcript (visual-only content)
- Align transcript into windows (10–20s).
- Embed both transcript windows and extracted visual payloads into the same embedding space.
- If similarity below threshold → mark visual-only gap.

This is standard cross-modal retrieval logic used in Video-RAG systems.

Output: gaps[] with timestamps + extracted data.

### 7) Index + serve

Store everything as:
{timestamp, artifact_type, raw_frame_path, extracted_structured, short_summary, gap_flag}
into a vector DB + file store. Enables later "ask questions about video" workflows.

⸻

## Top "reference architectures" (pick your flavor)

### A) Classic CV + Specialists + LLM reasoning (most faithful)

Shot/slide detect → keyframes → classifier → DePlot/TATR/OCR → LLM summaries
- **Best for**: correctness, numbers, tables, legal/tech vids.
- **Tradeoff**: more components, but each is simple.

### B) VLM-centric with grounding + verification (lowest friction if it behaves)

Shot detect → keyframes → VLM classify → VLM extract w/ "evidence-only" prompt → verify against OCR/DePlot when relevant
- **Best for**: fast iteration, wide domains.
- **Tradeoff**: still needs guardrails. Grounded models like VideoGLaMM help if you later want pixel-linked evidence.

### C) Hybrid open-vocab detection + VLM reasoning (SOTA efficiency)

Shot detect → keyframes → open-vocab detect (charts/tables/screens) → specialists → VLM explain
- **Best for**: long videos; compute control.
- **Tradeoff**: add one detector dependency. MVP-style keyframe-only detection is proven to keep accuracy while slashing cost.

⸻

## Blunt take on model choices (2025 reality)

- **Gemma Vision is fine**, but not the best for doc-style OCR + slide parsing.
- **Qwen2.5-VL / InternVL2.5** are widely used open models for OCR-heavy, long-video understanding now, and have tooling for video captioning.

So yeah… try them as drop-in for your "light classifier" step even if you keep Gemma for something else.

⸻

## ⚡ Next-Right Move (one concrete step)

Build Module 4 (light artifact classifier) first.
Do a dry run on 1 video and output a CSV:
timestamp, artifact_type, confidence.

Once that's stable, everything else becomes boring plumbing instead of chaos.

If you want, paste your current keyframe extractor + a couple Gemma outputs, and I'll sketch a minimal prompt set + a thresholding rule that fits your exact domain.