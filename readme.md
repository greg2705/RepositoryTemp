from transformers import AutoProcessor, AutoModelForCTC

processor = AutoProcessor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-english")

model = AutoModelForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-english")
