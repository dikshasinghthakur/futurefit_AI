import { useId } from 'react';
import { motion } from 'framer-motion';
import { spring } from '../lib/motion';

export default function Segmented({ options, value, onChange, label }) {
  const group = useId();
  return (
    <div className="segmented" role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" role="radio" aria-checked={value === o.value} className={value === o.value ? 'on' : ''} onClick={() => onChange(o.value)}>
          {value === o.value && <motion.span layoutId={`seg-${group}`} className="seg-pill" transition={spring} />}
          {o.label}
        </button>
      ))}
    </div>
  );
}
