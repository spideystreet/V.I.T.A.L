import { ScrollView, StyleSheet, Text } from 'react-native';

interface Props {
  text: string;
}

export function TranscriptView({ text }: Props) {
  if (!text) return null;
  return (
    <ScrollView style={styles.box}>
      <Text style={styles.text}>{text}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  box: {
    width: '100%',
    backgroundColor: '#1a1a1a',
    borderRadius: 14,
    padding: 16,
    maxHeight: 300,
  },
  text: { color: '#e2e8f0', fontSize: 16, lineHeight: 26 },
});
