import { motion } from 'framer-motion';

export default function EmptyState({ icon: Icon, title, text, action }) {
  return (
    <motion.div className="card empty" initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.35 }}>
      <div className="empty-icon"><Icon size={28} /></div>
      <h2>{title}</h2>
      {text && <p className="muted" style={{ maxWidth: 420 }}>{text}</p>}
      {action}
    </motion.div>
  );
}
