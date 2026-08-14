def _merge_voice_features(self, data_frames: List):
    if self.voice_features:
        data_frames.append(pl.LazyFrame(self.voice_features.model_dump()))
