export default function Importance({ weight }) {
  return (
    <span className="dots" title={`Importance ${weight}/5`} aria-label={`Importance ${weight} of 5`}>
      {[1, 2, 3, 4, 5].map((n) => <i key={n} className={n <= weight ? 'on' : ''} />)}
    </span>
  );
}
