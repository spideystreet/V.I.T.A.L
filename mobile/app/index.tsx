import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Link } from 'expo-router';
import { useNotifications } from '../hooks/useNotifications';

export default function HomeScreen() {
  useNotifications();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>VITAL</Text>
      <Text style={styles.subtitle}>Vocal health tracker</Text>

      <Link href="/checkup" asChild>
        <Pressable style={styles.btn}>
          <Text style={styles.btnText}>🎙 Démarrer le checkup</Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f0f', alignItems: 'center', justifyContent: 'center', padding: 24, gap: 24 },
  title: { fontSize: 40, fontWeight: '800', color: '#fff' },
  subtitle: { fontSize: 16, color: '#888' },
  btn: { backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 18, paddingHorizontal: 32, alignItems: 'center', width: '100%' },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
