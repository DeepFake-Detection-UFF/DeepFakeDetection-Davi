from pathlib import Path
import random
import cv2
import requests
from tqdm import tqdm
from typing import List
import numpy as np

def download_and_prepare_faceforensics(
    technique: str,
    num_videos: int,
    num_frames_per_video: int = 10,
    split_ratio: float = 0.8,
    base_url: str = "https://github.com/streamlink/streamlink/raw/master/tests/stream", # test URL for demonstration
    output_dir: Path = Path("./data/raw/faceforensics"),
):

    technique = technique.lower()
    video_ids = [f"{technique}.mp4" for _ in range(num_videos)]
    random.shuffle(video_ids)

    split_index = int(len(video_ids) * split_ratio)
    train_videos = video_ids[:split_index]
    test_videos = video_ids[split_index:]

    for subset, video_list in [("train", train_videos), ("test", test_videos)]:
        for video_name in tqdm(video_list, desc=f"Processando {subset}"):
            url = f"{base_url}/{video_name}"
            local_video_dir = output_dir / "videos" / technique
            local_video_dir.mkdir(parents=True, exist_ok=True)
            video_path = local_video_dir / video_name

            try:
                if not video_path.exists():
                    print(f"Baixando {url} ...")
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(video_path, "wb") as f:
                        f.write(response.content)
                else:
                    print(f"{video_path} já existe. Pulando download.")
            except Exception as e:
                print(f"Erro ao baixar {url}: {e}")
                continue

            frames = extract_random_frames(str(video_path), num_frames=num_frames_per_video)

            subset_dir = output_dir / subset / technique
            subset_dir.mkdir(parents=True, exist_ok=True)

            for idx, frame in enumerate(frames):
                filename = f"{video_name.replace('.mp4', '')}_{idx}.jpg"
                cv2.imwrite(str(subset_dir / filename), frame)

def extract_random_frames(video_path: str, num_frames: int = 10, resize_to=(256, 256)) -> List[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    frames = []

    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return frames

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return frames

    num_frames = min(num_frames, total_frames)
    indices = sorted(random.sample(range(total_frames), num_frames))

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            if resize_to:
                frame = cv2.resize(frame, resize_to)
            frames.append(frame)

    cap.release()
    return frames