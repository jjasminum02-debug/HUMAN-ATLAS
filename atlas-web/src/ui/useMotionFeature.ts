import { useEffect, useState } from 'react';
import { retryableResource } from '../domain/retryableResource';
import type * as MotionFeature from './motionFeature';

const loadMotionFeature = retryableResource(() => import('./motionFeature'));
export function useMotionFeature(needed: boolean) {
  const [feature, setFeature] = useState<typeof MotionFeature | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    if (!needed || feature) return;
    let active = true;
    setFailed(false);
    void loadMotionFeature().then(value => { if (active) setFeature(value); })
      .catch(() => { if (active) setFailed(true); });
    return () => { active = false; };
  }, [needed, feature]);
  // Browsers can cache a rejected module import. Explicit refresh also recovers
  // a stale deployment URL; never automatically reload a learner's active scene.
  return { feature, failed, reload: () => window.location.reload() };
}
