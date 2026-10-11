import { useId } from 'react';
import { motion } from 'framer-motion';
import AnimatedNumber from './AnimatedNumber';

export default function ScoreRing({ value = 0, size = 180, stroke = 14, label, sublabel }) {
  const id = useId();
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value));

  return (
    <div className="ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }} role="img" aria-label={`${Math.round(pct)} percent`}>
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="var(--accent)" />
            <stop offset="100%" stopColor="var(--accent-2)" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--bg-soft)" strokeWidth={stroke} />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke={`url(#${id})`} strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c * (1 - pct / 100) }}
          transition={{ duration: 1.3, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="ring-label">
        <div style={{ fontSize: size * 0.24, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1 }}>
          <AnimatedNumber value={pct} decimals={0} suffix="%" />
        </div>
        {label && <div style={{ fontWeight: 650, marginTop: 4, fontSize: size * 0.085 }}>{label}</div>}
        {sublabel && <div className="muted" style={{ fontSize: size * 0.07 }}>{sublabel}</div>}
      </div>
    </div>
  );
}
