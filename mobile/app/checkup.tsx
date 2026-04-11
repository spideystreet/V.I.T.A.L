import { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { VoiceButton } from '../components/VoiceButton';
import { TranscriptView } from '../components/TranscriptView';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';

export default function CheckupScreen() {
  const [transcript, setTranscript] = useState('');
  const { state, start, stop } = useVoiceRecorder((text) => setTranscript((prev) => prev + '\n' + text));

  return (
    <View style={styles.container}>
      <VoiceButton state={state} onPress={state === 'idle' ? start : stop} />
      <TranscriptView text={transcript.trim()} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f0f', padding: 24, gap: 20, justifyContent: 'center' },
});
