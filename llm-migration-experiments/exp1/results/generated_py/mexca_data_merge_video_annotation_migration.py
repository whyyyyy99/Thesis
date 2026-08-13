import polars as pl
from typing import List


def _merge_video_annotation(self, data_frames: List[pl.DataFrame]):
    if self.video_annotation:
        video_annotation_dict = self.video_annotation.model_dump()
        del video_annotation_dict["face_average_embeddings"]
        data_frames.append(pl.DataFrame(video_annotation_dict))
