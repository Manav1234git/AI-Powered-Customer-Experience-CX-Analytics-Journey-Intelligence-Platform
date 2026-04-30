import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [formData, setFormData] = useState({
    customer_id: '',
    name: '',
    text: '',
    rating: 5,
    date: new Date().toISOString().split('T')[0]
  });
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const res = await axios.get(`${API_URL}/reviews`);
      setReviews(res.data);
    } catch (error) {
      console.error("Error fetching reviews", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/submit-review`, formData);
      setSuccessMsg('Review submitted successfully!');
      setFormData({ ...formData, text: '', customer_id: '', name: '' });
      fetchReviews();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (error) {
      console.error("Error submitting review", error);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Customer Reviews</h2>
        <p className="text-textSecondary">Submit new feedback and view live sentiment analysis</p>
      </div>

      <div className="bg-card p-6 rounded-xl border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">Add New Review</h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input required type="text" placeholder="Customer ID (e.g. C011)" className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" value={formData.customer_id} onChange={e => setFormData({...formData, customer_id: e.target.value})} />
            <input required type="text" placeholder="Customer Name" className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
          </div>
          <textarea required placeholder="Review Text..." className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-white min-h-[100px]" value={formData.text} onChange={e => setFormData({...formData, text: e.target.value})}></textarea>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" value={formData.rating} onChange={e => setFormData({...formData, rating: parseInt(e.target.value)})}>
              {[5,4,3,2,1].map(num => <option key={num} value={num}>{num} Stars</option>)}
            </select>
            <input required type="date" className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} />
          </div>
          <button type="submit" className="bg-accent hover:bg-blue-600 text-white py-3 px-6 rounded-lg font-medium transition-colors">Submit Review</button>
          {successMsg && <div className="text-success text-sm font-medium mt-2">{successMsg}</div>}
        </form>
      </div>

      <div className="bg-card p-6 rounded-xl border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">Live Review Stream</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-textSecondary text-sm">
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4 w-1/2">Review</th>
                <th className="py-3 px-4">Rating</th>
                <th className="py-3 px-4">Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map(review => (
                <tr key={review.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                  <td className="py-3 px-4 text-sm whitespace-nowrap">{review.date}</td>
                  <td className="py-3 px-4">
                    <div className="font-medium text-textPrimary">{review.name}</div>
                    <div className="text-xs text-textSecondary">{review.customer_id}</div>
                  </td>
                  <td className="py-3 px-4 text-sm text-textSecondary line-clamp-2">{review.text}</td>
                  <td className="py-3 px-4 text-sm">{review.rating} / 5</td>
                  <td className="py-3 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      review.sentiment_label === 'Positive' ? 'bg-green-500/20 text-green-400' :
                      review.sentiment_label === 'Negative' ? 'bg-red-500/20 text-red-400' :
                      'bg-slate-500/20 text-slate-400'
                    }`}>
                      {review.sentiment_label}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
