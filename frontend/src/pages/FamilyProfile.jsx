import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../AuthContext';
import api from '../api';

export default function FamilyProfile() {
  const { user } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [newMember, setNewMember] = useState({
    full_name: '', date_of_birth: '', gender: 'MALE', relationship_to_head: 'SON', occupation: '', education: ''
  });

  const fetchProfile = async () => {
    try {
      const res = await api.get('/family/profile');
      setProfile(res.data);
    } catch (err) {
      console.error("Failed to load profile", err);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleAddMember = async (e) => {
    e.preventDefault();
    try {
      await api.post('/family/members', newMember);
      alert('Member added successfully!');
      fetchProfile(); // Refresh the list
      setNewMember({ full_name: '', date_of_birth: '', gender: 'MALE', relationship_to_head: 'SON', occupation: '', education: '' });
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to add member');
    }
  };

  if (!profile) return <div>Loading profile...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Family Profile: {profile.family_id}</h2>
      <p><strong>Address:</strong> {profile.address}, {profile.village}, {profile.taluka}, {profile.district}</p>
      <p><strong>Annual Income:</strong> ₹{profile.annual_income}</p>

      <hr />
      <h3>Add Family Member</h3>
      <form onSubmit={handleAddMember} style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
        <input type="text" placeholder="Full Name" value={newMember.full_name} onChange={e => setNewMember({...newMember, full_name: e.target.value})} required />
        <input type="date" value={newMember.date_of_birth} onChange={e => setNewMember({...newMember, date_of_birth: e.target.value})} required />
        <select value={newMember.gender} onChange={e => setNewMember({...newMember, gender: e.target.value})}>
          <option value="MALE">Male</option>
          <option value="FEMALE">Female</option>
          <option value="OTHER">Other</option>
        </select>
        <select value={newMember.relationship_to_head} onChange={e => setNewMember({...newMember, relationship_to_head: e.target.value})}>
          <option value="HEAD">Head</option>
          <option value="SPOUSE">Spouse</option>
          <option value="SON">Son</option>
          <option value="DAUGHTER">Daughter</option>
        </select>
        <button type="submit" style={{ background: '#28a745', color: 'white', border: 'none', padding: '8px 16px' }}>Add</button>
      </form>

      <h3>Registered Members</h3>
      <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#f4f4f4' }}>
            <th>Name</th>
            <th>DOB</th>
            <th>Gender</th>
            <th>Relation</th>
          </tr>
        </thead>
        <tbody>
          {profile.members.map(m => (
            <tr key={m.member_id} style={{ borderBottom: '1px solid #ddd' }}>
              <td>{m.full_name}</td>
              <td>{m.date_of_birth}</td>
              <td>{m.gender}</td>
              <td>{m.relationship}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}