import { useEffect } from 'react';
import { animate, motion, useMotionValue, useReducedMotion, useTransform } from 'framer-motion';

export default function AnimatedNumber({ value, decimals = 0, suffix = '', duration = 1.1 }) {
  const reduce = useReducedMotion();
  const mv = useMotionValue(0);
  const text = useTransform(mv, (v) => `${v.toFixed(decimals)}${suffix}`);

  useEffect(() => {
    const target = Number(value) || 0;
    if (reduce) { mv.set(target); return undefined; }
    const controls = animate(mv, target, { duration, ease: [0.22, 1, 0.36, 1] });
    return () => controls.stop();
  }, [value, reduce, duration, mv]);

  return <motion.span>{text}</motion.span>;
}
