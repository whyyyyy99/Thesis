import polars as pl
from typing import List

def _merge_voice_features(self, data_frames: List):
    if self.voice_features:
        data_frames.append(pl.DataFrame(self.voice_features.model_dump()))