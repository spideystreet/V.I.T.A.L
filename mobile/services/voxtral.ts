import { MISTRAL_API_KEY } from '../constants/config';

export async function transcribeAudio(uri: string): Promise<string> {
  const formData = new FormData();
  formData.append('model', 'voxtral-mini-latest');
  formData.append('language', 'fr');
  formData.append('file', { uri, name: 'recording.m4a', type: 'audio/m4a' } as any);

  const res = await fetch('https://api.mistral.ai/v1/audio/transcriptions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${MISTRAL_API_KEY}` },
    body: formData,
  });

  const json = await res.json();
  if (!res.ok) throw new Error(json.error?.message ?? `HTTP ${res.status}`);
  return json.text as string;
}
