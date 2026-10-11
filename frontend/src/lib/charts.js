import { useEffect, useState } from 'react';
import {
  Chart as ChartJS, ArcElement, BarElement, CategoryScale, Filler, Legend, LineElement,
  LinearScale, PointElement, RadialLinearScale, Tooltip,
} from 'chart.js';

ChartJS.register(ArcElement, BarElement, CategoryScale, Filler, Legend, LineElement, LinearScale, PointElement, RadialLinearScale, Tooltip);
ChartJS.defaults.font.family = "'Inter', system-ui, sans-serif";
ChartJS.defaults.animation = { duration: 900, easing: 'easeOutQuart' };
ChartJS.defaults.maintainAspectRatio = false;
ChartJS.defaults.plugins.legend.display = false;

export const alpha = (hex, a) => {
  const h = hex.replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map((c) => c + c).join('') : h, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

const read = () => {
  const cs = getComputedStyle(document.documentElement);
  const g = (n) => cs.getPropertyValue(n).trim();
  return { text: g('--muted'), grid: g('--border'), accent: g('--accent'), accent2: g('--accent-2'), ok: g('--ok'), warn: g('--warn'), bad: g('--bad'), card: g('--bg-elev') };
};

/** Chart.js can't read CSS variables, so re-read them whenever the theme attribute changes. */
export function useChartColors() {
  const [colors, setColors] = useState(read);
  useEffect(() => {
    const obs = new MutationObserver(() => setColors(read()));
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => obs.disconnect();
  }, []);
  return colors;
}

export const tooltipStyle = (c) => ({
  backgroundColor: c.card, titleColor: c.text, bodyColor: c.text, borderColor: c.grid, borderWidth: 1,
  padding: 10, cornerRadius: 10, displayColors: false,
});
