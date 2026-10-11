import { Link } from 'react-router-dom';
import { Compass } from 'lucide-react';
import EmptyState from '../components/EmptyState.jsx';

export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 20 }}>
      <EmptyState icon={Compass} title="This page took a wrong turn" text="The page you're looking for doesn't exist or has moved."
        action={<Link to="/" className="btn btn-primary">Back to home</Link>} />
    </div>
  );
}
