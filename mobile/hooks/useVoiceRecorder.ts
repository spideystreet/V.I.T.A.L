import { useState, useRef } from 'react';
import { Audio } from 'expo-av';
import { transcribeAudio } from '../services/voxtral';

type State = 'idle' | 'recording' | 'transcribing';

export function useVoiceRecorder(onTranscript: (text: string) => void) {
  const [state, setState] = useState<State>('idle');
  const [error, setError] = useState<string | null>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);

  async function start() {
    setError(null);
    await Audio.requestPermissionsAsync();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
    const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
    recordingRef.current = recording;
    setState('recording');
  }

  async function stop() {
    const recording = recordingRef.current;
    if (!recording) return;
    setState('transcribing');
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI()!;
    recordingRef.current = null;
    try {
      const text = await transcribeAudio(uri);
      onTranscript(text);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setState('idle');
    }
  }

  return { state, error, start, stop };
}
