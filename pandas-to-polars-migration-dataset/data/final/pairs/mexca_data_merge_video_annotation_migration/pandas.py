import pandas as pd

    def _merge_video_annotation(self, data_frames: List[pd.DataFrame]):
        if self.video_annotation:
            video_annotation_dict = self.video_annotation.model_dump()
            del video_annotation_dict["face_average_embeddings"]
            data_frames.append(pd.DataFrame(video_annotation_dict))
