import pandas as pd

def _merge_audio_text_features(self, data_frames: List[pd.DataFrame]):
    # ...
    audio_text_features_df = pd.DataFrame(audio_annotation_dict)
    if self.transcription and self.transcription.segments:
        text_features_df = pd.DataFrame(text_features_dict)
        if self.sentiment and self.sentiment.segments:
            text_features_df = text_features_df.merge(
                pd.DataFrame(sentiment_dict),
                on=["frame", "span_text"],
                how="left",
            )

        audio_text_features_df = audio_text_features_df.merge(
            text_features_df,
            on=["frame", "segment_speaker_label"],
            how="left",
        )
    data_frames.append(audio_text_features_df)
