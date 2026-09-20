import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../AuthContext';
import api from '../api';

export default function Schemes() {
  const { user } = useContext(AuthContext);
  const [schemes, setSchemes] = useState([]);
  const [members, setMembers] = useState([]);
  const [selectedMember, setSelectedMember] = useState('');

  useEffect(() => {
    const loadData = async () => {
      const schemeRes = await api.get('/schemes');
      setSchemes(schemeRes.data);
      
      if (user.family_id) {
        const profileRes = await api.get('/family/profile');
        setMembers(profileRes.data.members);
      }
    };
    loadData();
  }, [user.family_id]);

  const handleApply = async (scheme) => {
    if (scheme.beneficiary_type === 'MEMBER' && !selectedMember) {
      alert('Please select a family member for this scheme.');
      return;
    }

    try {
      const payload = { 
        scheme_id: scheme.scheme_id, 
        member_id: scheme.beneficiary_type === 'MEMBER' ? selectedMember : null 
      };
      
      // Step 1: Check Eligibility
      const check = await api.post(`/schemes/${scheme.scheme_id}/check-eligibility`, payload);
      
      if (!check.data.eligible) {
        alert("Not Eligible:\n" + check.data.reasons.join("\n"));
        return;
      }

      // Step 2: Apply
      await api.post('/applications', payload);
      alert('Application submitted successfully!');
    } catch (err) {
      alert(err.response?.data?.message || 'Application failed');
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Government Schemes</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <label><strong>Select Member (for individual schemes): </strong></label>
        <select value={selectedMember} onChange={(e) => setSelectedMember(e.target.value)}>
          <option value="">-- Select Member --</option>
          {members.map(m => (
            <option key={m.member_id} value={m.member_id}>{m.full_name}</option>
          ))}
        </select>
      </div>

      <div style={{ display: 'grid', gap: '15px' }}>
        {schemes.map(s => (
          <div key={s.scheme_id} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
            <h3>{s.scheme_name}</h3>
            <p><strong>Type:</strong> {s.beneficiary_type}</p>
            <button 
              onClick={() => handleApply(s)} 
              style={{ background: '#007bff', color: 'white', padding: '8px 16px', border: 'none', cursor: 'pointer' }}
            >
              Check Eligibility & Apply
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}