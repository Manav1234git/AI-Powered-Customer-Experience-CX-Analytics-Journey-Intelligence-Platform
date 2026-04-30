import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function Analytics() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setUploadStatus('Uploading data...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await axios.post(`${API_URL}/upload-data`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus('Analyzing data...');
      
      const res = await axios.post(`${API_URL}/analyze-data`);
      setAnalysisResults(res.data.results);
      setUploadStatus('Analysis complete!');
    } catch (error) {
      console.error(error);
      setUploadStatus('Error during upload or analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Deep Data Analytics</h2>
        <p className="text-textSecondary">Upload bulk CSV or JSON datasets for comprehensive AI analysis</p>
      </div>

      <div className="bg-card p-8 rounded-xl border border-slate-700 text-center flex flex-col items-center justify-center gap-4">
        <div className="w-20 h-20 rounded-full bg-slate-800 flex items-center justify-center border-2 border-dashed border-slate-600">
          <UploadCloud size={32} className="text-blue-400" />
        </div>
        <div>
          <h3 className="text-lg font-medium">Upload Dataset</h3>
          <p className="text-sm text-textSecondary mt-1">Drag and drop or click to select CSV/JSON</p>
        </div>
        <input type="file" accept=".csv,.json" onChange={handleFileChange} className="mt-4 text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500/20 file:text-blue-400 hover:file:bg-blue-500/30" />
        <button 
          onClick={handleUploadAndAnalyze} 
          disabled={!file || isAnalyzing}
          className="mt-4 bg-accent hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 px-8 rounded-lg font-medium transition-colors"
        >
          {isAnalyzing ? 'Processing...' : 'Run Analysis'}
        </button>
        {uploadStatus && <p className="text-sm mt-2 text-blue-400">{uploadStatus}</p>}
      </div>

      {analysisResults && (
        <div className="bg-card p-6 rounded-xl border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2"><FileText size={20} /> Analysis Report</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-sm text-textSecondary mb-3">Summary Stats</h4>
              <div className="bg-slate-900 p-4 rounded-lg flex flex-col gap-2">
                <div className="flex justify-between"><span>Rows Analyzed</span> <span className="font-bold">{analysisResults.total_analyzed}</span></div>
                <div className="flex justify-between"><span>Positive Sentiment</span> <span className="font-bold text-green-400">{analysisResults.sentiment_distribution.Positive}%</span></div>
                <div className="flex justify-between"><span>Neutral Sentiment</span> <span className="font-bold text-slate-400">{analysisResults.sentiment_distribution.Neutral}%</span></div>
                <div className="flex justify-between"><span>Negative Sentiment</span> <span className="font-bold text-red-400">{analysisResults.sentiment_distribution.Negative}%</span></div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm text-textSecondary mb-3">Detected Topics</h4>
              <div className="flex flex-wrap gap-2">
                {analysisResults.top_topics.map(topic => (
                  <span key={topic} className="px-3 py-1 bg-blue-500/20 border border-blue-500/30 text-blue-300 rounded-full text-sm">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
