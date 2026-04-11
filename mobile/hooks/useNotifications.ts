import { useEffect, useState } from 'react';
import { requestPermissions } from '../services/notifications';

export function useNotifications() {
  const [granted, setGranted] = useState(false);

  useEffect(() => {
    requestPermissions().then(setGranted);
  }, []);

  return { granted };
}
