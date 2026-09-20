import React, { useState, useEffect } from 'react';
import api from '../api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [duplicates, setDuplicates] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await api.get('/admin/dashboard');
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load admin stats", err);
    }
  };

  const handleDuplicateCheck = async () => {
    try {
      const res = await api.get('/admin/duplicate-check');
      setDuplicates(res.data);
    } catch (err) {
      alert('Failed to run duplicate check');
    }
  };

  if (!stats) return <div>Loading Admin Panel...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Admin Dashboard</h2>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <div style={{ padding: '20px', background: '#f8f9fa', border: '1px solid #ddd' }}>
          <h4>Total Families</h4>
          <h2>{stats.total_families}</h2>
        </div>
        <div style={{ padding: '20px', background: '#f8f9fa', border: '1px solid #ddd' }}>
          <h4>Total Members</h4>
          <h2>{stats.total_members}</h2>
        </div>
        <div style={{ padding: '20px', background: '#fff3cd', border: '1px solid #ffeeba' }}>
          <h4>Pending Applications</h4>
          <h2>{stats.pending_applications}</h2>
        </div>
        <div style={{ padding: '20px', background: '#d4edda', border: '1px solid #c3e6cb' }}>
          <h4>Active Benefits</h4>
          <h2>{stats.active_benefits}</h2>
        </div>
      </div>

      <button 
        onClick={handleDuplicateCheck}
        style={{ padding: '10px 20px', background: '#dc3545', color: 'white', border: 'none', cursor: 'pointer' }}
      >
        Run Duplicate Record Scan
      </button>

      {duplicates && (
        <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #dc3545' }}>
          <h3>Duplicate Scan Results: Found {duplicates.duplicates_found}</h3>
          <ul>
            {duplicates.records.map((dup, idx) => (
              <li key={idx}>
                <strong>{dup.full_name}</strong> (DOB: {dup.date_of_birth}) appears {dup.duplicate_count} times across the system.
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}