rom pyannote.audio.pipelines import VoiceActivityDetection
pipeline = VoiceActivityDetection(segmentation=model)
HYPER_PARAMETERS = {
  "onset": 0.5, "offset": 0.5,
  "min_duration_on": 0.0,
  
  "min_duration_off": 0.0
}
pipeline.instantiate(HYPER_PARAMETERS)
vad = pipeline("audio.wav")


from pyannote.audio.pipelines import OverlappedSpeechDetection
pipeline = OverlappedSpeechDetection(segmentation=model)
pipeline.instantiate(HYPER_PARAMETERS)
osd = pipeline("audio.wav")
