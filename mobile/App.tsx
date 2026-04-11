import { useState } from 'react';
import { View, Text, Pressable, StyleSheet, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

const STEPS = [
  {
    emoji: '👋',
    title: 'Bienvenue sur VITAL',
    desc: 'Ton assistant santé vocal. On analyse ta voix et tes données biométriques pour détecter le burnout avant qu\'il arrive.',
  },
  {
    emoji: '🎙',
    title: 'Parle, on écoute',
    desc: 'Chaque semaine, 3 questions. 3 minutes. VITAL croise ta réponse vocale avec tes données de sommeil, rythme cardiaque et stress.',
  },
  {
    emoji: '📊',
    title: 'Tes données, ton tableau de bord',
    desc: 'Toutes tes métriques santé au même endroit. Tendances sur 7 jours, alertes biométriques, score de récupération.',
  },
  {
    emoji: '🔔',
    title: 'Des nudges, pas du bruit',
    desc: 'VITAL t\'envoie une notification uniquement quand tes signaux biométriques le justifient. Pas de spam.',
  },
];

export default function App() {
  const [step, setStep] = useState(0);
  const isLast = step === STEPS.length - 1;
  const current = STEPS[step];

  return (
    <View style={styles.container}>
      <View style={styles.dots}>
        {STEPS.map((_, i) => (
          <View key={i} style={[styles.dot, i === step && styles.dotActive]} />
        ))}
      </View>

      <Text style={styles.emoji}>{current.emoji}</Text>
      <Text style={styles.title}>{current.title}</Text>
      <Text style={styles.desc}>{current.desc}</Text>

      <View style={styles.actions}>
        {step > 0 && (
          <Pressable style={styles.btnSecondary} onPress={() => setStep(step - 1)}>
            <Text style={styles.btnSecondaryText}>Retour</Text>
          </Pressable>
        )}
        <Pressable style={[styles.btn, step === 0 && styles.btnFull]} onPress={() => setStep(step + 1)} disabled={isLast}>
          <Text style={styles.btnText}>{isLast ? '✅ C\'est parti !' : 'Suivant'}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f0f', alignItems: 'center', justifyContent: 'center', padding: 32, gap: 24 },
  dots: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#333' },
  dotActive: { backgroundColor: '#6366f1', width: 24 },
  emoji: { fontSize: 64 },
  title: { fontSize: 28, fontWeight: '800', color: '#fff', textAlign: 'center' },
  desc: { fontSize: 16, color: '#888', textAlign: 'center', lineHeight: 24 },
  actions: { flexDirection: 'row', gap: 12, width: '100%', marginTop: 16 },
  btn: { flex: 1, backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 18, alignItems: 'center' },
  btnFull: { flex: 1 },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  btnSecondary: { flex: 1, backgroundColor: '#1a1a1a', borderRadius: 14, paddingVertical: 18, alignItems: 'center' },
  btnSecondaryText: { color: '#888', fontWeight: '600', fontSize: 16 },
});
