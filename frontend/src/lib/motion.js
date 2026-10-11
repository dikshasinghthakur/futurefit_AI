export const ease = [0.22, 1, 0.36, 1];

export const pageVariants = {
  initial: { opacity: 0, y: 14 },
  enter: { opacity: 1, y: 0, transition: { duration: 0.35, ease } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.18, ease: 'easeIn' } },
};

export const stagger = (delay = 0.06, start = 0) => ({
  hidden: {},
  show: { transition: { staggerChildren: delay, delayChildren: start } },
});

export const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease } },
};

export const pop = {
  hidden: { opacity: 0, scale: 0.85 },
  show: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 380, damping: 24 } },
};

export const spring = { type: 'spring', stiffness: 420, damping: 30 };
