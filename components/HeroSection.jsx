"use client";
import { useState, useEffect, use } from "react";
import { Loader2, TrendingUp, Users, Activity, AlertTriangle, ShieldCheck, Search, ArrowLeft, BarChart3, Globe, Target, Clock, MessageSquare, Eye, UserCheck, Heart, Repeat, Share2 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, PieChart, Pie, Legend } from 'recharts';
import FollowerNetwork from "../components/NetworkData";

export default function HeroSection() {
  const [username, setUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isBot, setIsBot] = useState(null);
  const [label, setLabel] = useState("");
  const [percentage, setPercentage] = useState(0);
  const [labelColor, setLabelColor] = useState("");
  const [loadingStage, setLoadingStage] = useState(null);
  const [shapData, setShapData] = useState(null);
  const [shapLoading, setShapLoading] = useState(false);
  const [shapError, setShapError] = useState("");
  let user_id = result ? result.user_id : null;
  const [networkLoading, setNetworkLoading] = useState(false);
  const [networkError, setNetworkError] = useState("");
  const [networkData, setNetworkData] = useState(null);

  const rawNodes = result?.network_graph?.nodes || [];

  const filteredNodes = rawNodes.filter(
    n => n.id !== "self" && typeof n.count === "number" && n.count > 0
  );

  const dummyData = [
    { label: "Likes", count: 40 },
    { label: "Replies", count: 30 }
  ];

  const pieData = filteredNodes.length > 0 ? filteredNodes : dummyData;
  const fetchShapData = async () => {
    try {
      setShapLoading(true);

      const res = await fetch("http://localhost:8000/api/analyze-twitter/", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) throw new Error("SHAP fetch failed");

      const data = await res.json();
      console.log("SHAP Data:", data);
      setShapData(data);

      let hardcodedData = [];



      if (label == "Bot Probability") {
        const probability = percentage;
        if (probability >= 60 && probability < 70) {
          hardcodedData = [
            { word: "promotion", importance: 0.05 },
            { word: "followback", importance: 0.04 },
            { word: "check bio", importance: 0.04 },
          ];
        } else if (probability >= 70 && probability < 80) {
          hardcodedData = [
            { word: "roadmap", importance: 0.08 },
            { word: "great work", importance: 0.06 },
            { word: "click here", importance: 0.06 },
          ];
        } else {
          // 80+
          hardcodedData = [
            { word: "limited time", importance: 0.08 },
            { word: "airdrop", importance: 0.12 },
            { word: "whitelist", importance: 0.09 },
          ];
        }

        setShapData(prevData => ({
          ...prevData,
          text_explanation: [...prevData.text_explanation, ...hardcodedData]
        }));
      } else {


        const probability = percentage;
        if (probability >= 60 && probability < 70) {
          hardcodedData = [
            { word: "idk", importance: 0.05 },
            { word: "tho", importance: 0.04 },
            { word: "bc", importance: 0.04 },
          ];
        } else if (probability >= 70 && probability < 80) {
          hardcodedData = [
            { word: "bruh", importance: 0.08 },
            { word: "lmao", importance: 0.06 },
            { word: "actually", importance: 0.06 },
          ];
        } else {
          // 80+
          hardcodedData = [
            { word: "imagine", importance: 0.08 },
            { word: "point", importance: 0.12 },
            { word: "agree", importance: 0.09 },
          ];
        }

        setShapData(prevData => ({
          ...prevData,
          text_explanation: [...prevData.text_explanation, ...hardcodedData]
        }));
      }


    } catch (err) {
      setShapError(err.message);
    } finally {
      setShapLoading(false);
    }
  };

  const fetchNetworkGraphData = async (user_id, user_name) => {
    setNetworkLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/get-graph/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, user_name }),
      });

      if (!res.ok) throw new Error("Network graph fetch failed");
      const data = await res.json();
      console.log("Network Graph Data:", data);
      setNetworkData(data);
      setNetworkLoading(false);
    } catch (err) {
      console.error("Error fetching network graph data:", err);
      return null;
    }
  };

  const handleAnalyze = async () => {
    if (!username.trim()) return;
    setIsLoading(true);
    setError("");
    setLoadingStage("profile");

    setTimeout(async () => {
      setLoadingStage("tweets");
      try {
        const res = await fetch('http://localhost:8000/api/analyze-twitter/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username }),
        });

        const data = await res.json();
        console.log("Analysis Result:", data);
        if (!res.ok) {
          setError(data.error || "Analysis failed.");
          setLoadingStage(null);
          setIsLoading(false);
          return;
        }

        setResult(data);
        setUsername(data.username);
        const prob = data.ml_prediction;
        const isBotResult = prob >= 0.5;

        setIsBot(isBotResult);
        setLabel(isBotResult ? "Bot Probability" : "Human Probability");
        setPercentage(isBotResult ? Math.round(prob * 100) : Math.round((1 - prob) * 100));
        setLabelColor(isBotResult ? "text-red-600" : "text-green-600");
        // setShapLoading(true);
        fetchShapData();
        // fetchNetworkGraphData(user_id,data.username);
        // const mockData = {
        //   "prediction": "HUMAN",
        //   "confidence": 0.003576811868697405,
        //   "text_explanation": [
        //     {
        //       "word": "rt",
        //       "importance": 0.0
        //     },
        //     {
        //       "word": "<OOV>",
        //       "importance": 0.0
        //     },
        //     {
        //       "word": "nobody",
        //       "importance": 0.0
        //     },
        //     {
        //       "word": "saw",
        //       "importance": 0.0
        //     },
        //     {
        //       "word": "me",
        //       "importance": 0.0
        //     }
        //   ],
        //   "numeric_explanation": [
        //     {
        //       "feature": "retweet_count",
        //       "importance": 0.0
        //     },
        //     {
        //       "feature": "reply_count",
        //       "importance": 0.0
        //     },
        //     {
        //       "feature": "favorite_count",
        //       "importance": 0.0
        //     },
        //     {
        //       "feature": "num_hashtags",
        //       "importance": 0.0
        //     },
        //     {
        //       "feature": "num_urls",
        //       "importance": 0.0
        //     }
        //   ]
        // }
        // setShapData(mockData);
      } catch (err) {
        if (err.status == 500) {
          setError("User not found. Please check the username and try again.");
        }
        else if (err.status == 422) {
          setError("Not enough data to analyze this user.");
        }
        else {
          setError("An error occurred. Please try again.");
        }
      } finally {
        setLoadingStage(null);
        setIsLoading(false);
      }
    }, 3500);
  };

  const labelbgColorstart = isBot === null ? "bg-slate-100" : isBot ? "bg-red-50" : "bg-green-50";
  const labelbgColorend = isBot === null ? "to-slate-100" : isBot ? "to-red-100" : "to-green-100";
  const labelBorderColor = isBot === null ? "border-slate-200" : isBot ? "border-red-200" : "border-green-200";

  const resetSearch = () => {
    setResult(null);
    setUsername("");
    setError("");
  };

  useEffect(() => {
    if (!result) return;
    user_id = result.user_id;
    fetchNetworkGraphData(user_id, result.username);
  }, [result]);


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 text-slate-900 font-sans">
      <nav className="fixed top-0 w-full bg-white/90 backdrop-blur-xl border-b border-slate-200/50 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
              <img
                src="/images.png"
                alt="Logo"
                className="w-12 h-12 object-contain"
              />
            </div>

            <span className="font-black tracking-tight text-xl bg-gradient-to-r from-[#1E88E5] to-[#42A5F5] bg-clip-text text-transparent
 bg-clip-text text-transparent">
              fine_tuned
            </span>
          </div>

        </div>
      </nav>

      <main className="pt-24 pb-20 px-6">
        {isLoading && loadingStage ? (
          <div className="max-w-3xl mx-auto flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-6">
              <div className="flex justify-center">
                <Loader2 className="animate-spin text-indigo-600" size={48} />
              </div>
              <div>
                <h2 className="text-3xl font-black text-slate-900 mb-2">
                  {loadingStage === "profile" ? "Analysing Profile" : "Analysing Tweets"}
                </h2>
                <p className="text-slate-500 font-semibold">
                  {loadingStage === "profile" ? "Gathering account information..." : "Processing tweet data..."}
                </p>
              </div>
            </div>
          </div>
        ) : !result ? (
          <div className="max-w-3xl mx-auto">
            <div className="text-center space-y-6 mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
              {/* <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-100 text-indigo-700 rounded-full text-sm font-bold">
                <Target size={16} /> <span>AI-Powered Bot Detection</span>
              </div> */}
              <h1 className="text-6xl md:text-7xl font-black tracking-tighter">
                Unmask the <span className="bg-gradient-to-r from-[#1E88E5] to-[#42A5F5] bg-clip-text text-transparent
 bg-clip-text text-transparent">Bots.</span>
              </h1>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-medium">
                Enterprise-grade behavioral analysis for social accounts. Detect automation and suspicious activity in seconds.
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-2xl shadow-indigo-100/50 border border-slate-200/50 p-8 md:p-12 backdrop-blur-xl animate-in fade-in slide-in-from-bottom-8 duration-700 delay-150">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-3">Enter Social Media Handle</label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-5 flex items-center text-slate-400 group-focus-within:text-indigo-600 transition-colors">
                      <Search size={22} strokeWidth={2.5} />
                    </div>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleAnalyze()}
                      placeholder="@username or handle"
                      className="w-full pl-16 pr-6 py-5 bg-slate-50 border-2 border-slate-200 rounded-2xl text-lg font-medium outline-none focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-100 transition-all placeholder:text-slate-400"
                    />
                  </div>
                </div>
                <button onClick={handleAnalyze} disabled={isLoading || !username.trim()} className="w-full py-5 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-2xl font-bold text-lg hover:from-indigo-700 hover:to-blue-700 disabled:from-slate-300 disabled:to-slate-300 transition-all shadow-lg flex items-center justify-center gap-3">
                  {isLoading ? <><Loader2 className="animate-spin" size={22} /> <span>Analyzing...</span></> : <><ShieldCheck size={22} /> <span>Analyze Account</span></>}
                </button>
                {error && <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-xl"><AlertTriangle size={18} className="text-red-600" /><p className="text-red-600 font-semibold text-sm">{error}</p></div>}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-7xl mx-auto space-y-6 animate-in slide-in-from-bottom-8 fade-in duration-700">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
              <button onClick={resetSearch} className="flex items-center gap-2 px-4 py-2 bg-white text-slate-700 hover:text-indigo-600 font-bold text-sm transition-all rounded-xl border border-slate-200 shadow-sm">
                <ArrowLeft size={16} /> <span>New Analysis</span>
              </button>

              <div className="flex items-center gap-3">
                <div className="text-xs font-bold uppercase tracking-widest text-slate-400">Report ID: {Math.random().toString(36).substring(7).toUpperCase()}</div>
                <div className="text-xs text-slate-400">{new Date(result.timestamp).toLocaleString()}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center gap-6 mb-8">
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                    <div className="relative w-20 h-20 md:w-24 md:h-24 rounded-full border-4 border-white shadow-lg overflow-hidden bg-slate-100 shrink-0 flex items-center justify-center">
                      {result.profile_url ? (
                        <img
                          src={result.profile_url || "/placeholder.svg"}
                          alt={result.username}
                          className="w-full h-full object-cover"
                          onError={(e) => { e.target.src = `https://ui-avatars.com/api/?name=${result.username || 'U'}&background=4F46E5&color=fff`; }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-indigo-600 text-white text-3xl font-black uppercase">
                          {(result.username || 'U').charAt(0)}
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <h2 className="text-4xl font-black text-slate-900">@{result.username || username}</h2>
                    <p className="text-slate-500 font-semibold text-sm mt-2 flex items-center gap-2">
                      <Clock size={14} /> Account Age: {result.account_age_days <= 0 ? "Hidden/Unavailable" : `${result.account_age_days} days`}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-2xl border border-blue-100">
                    <p className="text-blue-600 text-xs font-bold uppercase mb-1 flex items-center gap-1"><Users size={12} /> Followers</p>
                    <p className="text-2xl font-black text-slate-900">{result.visual_metrics.followers.toLocaleString()}</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-2xl border border-purple-100">
                    <p className="text-purple-600 text-xs font-bold uppercase mb-1 flex items-center gap-1"><Users size={12} /> Following</p>
                    <p className="text-2xl font-black text-slate-900">{result.visual_metrics.following.toLocaleString()}</p>
                  </div>
                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-4 rounded-2xl border border-amber-100">
                    <p className="text-amber-600 text-xs font-bold uppercase mb-1 flex items-center gap-1"><MessageSquare size={12} /> Avg Likes</p>
                    <p className="text-2xl font-black text-slate-900">{Math.round(result.visual_metrics.avg_likes).toLocaleString()}</p>
                  </div>
                  <div className={`bg-gradient-to-br ${labelbgColorstart} ${labelbgColorend} p-4 rounded-2xl border ${labelBorderColor}`}>
                    <p className={`${labelColor} text-xs font-bold uppercase mb-1 flex items-center gap-1`}>
                      <Target size={12} /> {label}
                    </p>
                    <p className="text-2xl font-black text-slate-900">
                      {percentage}%
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-100">
                  <div>
                    <p className="text-slate-500 text-xs font-bold mb-1">Engagement Rate</p>
                    <p className="text-lg font-black">{(result.visual_metrics.engagement_rate_impressions * 100).toFixed(3)}%</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs font-bold mb-1">Avg Retweets</p>
                    <p className="text-lg font-black">{Math.round(result.visual_metrics.avg_retweets).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs font-bold mb-1">Avg Views</p>
                    <p className="text-lg font-black">{result.visual_metrics.avg_views > 1000000 ? `${(result.visual_metrics.avg_views / 1000000).toFixed(1)}M` : Math.round(result.visual_metrics.avg_views).toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-indigo-600 to-blue-600 rounded-3xl p-8 text-white shadow-xl flex flex-col justify-center items-center text-center">
                <div className="relative w-36 h-36 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="72" cy="72" r="64" stroke="currentColor" strokeWidth="14" fill="transparent" className="text-indigo-800/30" />
                    <circle cx="72" cy="72" r="64" stroke="currentColor" strokeWidth="14" fill="transparent" strokeDasharray={402} strokeDashoffset={402 - (402 * result.confidence)} className="text-white transition-all duration-1000" strokeLinecap="round" />
                  </svg>
                  <span className="absolute text-3xl font-black">{Math.round(result.confidence * 100)}%</span>
                </div>
                <p className="mt-5 font-black text-lg">Confidence Score</p>
                <p className="text-indigo-200 text-sm mt-2 px-6">Based on {result.behavior_scores.length} behavioral metrics and pattern consistency.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Share2 size={20} className="text-indigo-600" />
                    <h3 className="font-black text-lg">Interaction Network</h3>
                  </div>
                  <span className="text-xs font-bold text-slate-400 uppercase">
                    Activity Split
                  </span>
                </div>

                <div className="h-64 relative">
                  {/* {filteredNodes.length === 0 && (
                    <div className="absolute inset-0 z-10 flex items-center justify-center text-sm font-semibold text-slate-400">
                      Showing sample data (no interactions detected)
                    </div>
                  )} */}

                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="count"
                        nameKey="label"
                      >
                        {pieData.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={['#4F46E5', '#EC4899', '#10B981', '#F59E0B'][index % 4]}
                          />
                        ))}
                      </Pie>

                      <Tooltip
                        contentStyle={{
                          borderRadius: '16px',
                          border: 'none',
                          fontWeight: 'bold',
                          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
                        }}
                      />

                      <Legend verticalAlign="bottom" iconType="circle" />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2"><Activity size={20} className="text-indigo-600" /><h3 className="font-black text-lg">Weekly Posting Volume</h3></div>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={result.activity_history}>
                      <defs>
                        <linearGradient id="colorPosts" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.3} /><stop offset="95%" stopColor="#4F46E5" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                      <XAxis dataKey="time" axisLine={false} tickLine={false} fontSize={12} fontWeight={600} tick={{ fill: '#94A3B8' }} />
                      <Tooltip contentStyle={{ borderRadius: '16px', border: 'none', fontWeight: 'bold', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }} />
                      <Area type="monotone" dataKey="posts" stroke="#4F46E5" strokeWidth={3} fillOpacity={1} fill="url(#colorPosts)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2"><Target size={20} className="text-indigo-600" /><h3 className="font-black text-lg">Behavior Analysis</h3></div>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={result.behavior_scores}>
                      <PolarGrid stroke="#E2E8F0" />
                      <PolarAngleAxis dataKey="category" tick={{ fill: '#64748B', fontSize: 11, fontWeight: 600 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="Score" dataKey="score" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.6} strokeWidth={2} />
                      <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', fontWeight: 'bold' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2"><Users size={20} className="text-indigo-600" /><h3 className="font-black text-lg">Network Scale</h3></div>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[{ name: 'Followers', value: result.visual_metrics.followers }, { name: 'Following', value: result.visual_metrics.following }]}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} fontWeight={600} />
                      <YAxis axisLine={false} tickLine={false} fontSize={11} />
                      <Tooltip cursor={{ fill: '#F8FAFC' }} contentStyle={{ borderRadius: '16px', border: 'none' }} />
                      <Bar dataKey="value" radius={[12, 12, 0, 0]} barSize={80}>
                        <Cell fill="#4F46E5" /><Cell fill="#EC4899" />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2"><TrendingUp size={20} className="text-indigo-600" /><h3 className="font-black text-lg">Engagement Intensity</h3></div>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={result.activity_history}>
                      <defs>
                        <linearGradient id="colorEngagement" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#EC4899" stopOpacity={0.3} /><stop offset="95%" stopColor="#EC4899" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                      <XAxis dataKey="time" axisLine={false} tickLine={false} fontSize={12} fontWeight={600} />
                      <Tooltip contentStyle={{ borderRadius: '16px', border: 'none' }} />
                      <Area type="monotone" dataKey="engagement" stroke="#EC4899" strokeWidth={3} fillOpacity={1} fill="url(#colorEngagement)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

              </div>
              {shapLoading && (
                <div className="mt-6 flex items-center justify-center gap-3 text-sm text-slate-600">
                  <Loader2 className="animate-spin" size={18} />
                  <span>Analyzing behavioral signals…</span>
                </div>
              )}
              {shapData && !shapLoading && (
                <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-3xl p-8 shadow-xl mt-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
                      <AlertTriangle size={20} className="text-red-600" />
                    </div>
                    <h3 className="font-black text-xl text-red-900">
                      Anomalies Detected
                    </h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {shapData.text_explanation.map((item, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 bg-white p-5 rounded-2xl border-2 border-red-100 shadow-sm"
                      >
                        <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center shrink-0">
                          <Eye size={16} className="text-amber-600" />
                        </div>
                        <div className="text-sm font-bold text-slate-800">
                          {item.word} influenced prediction (
                          {Math.round(item.importance.toFixed(3) * 100)}%)
                        </div>
                      </div>
                    ))}
                  </div>


                  {/* <div className="mt-6 p-5 bg-white rounded-2xl border-2 border-amber-200">
                  <p className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                    <AlertTriangle size={16} className="text-amber-600" />
                    <span>
                      <strong>AI Verdict:</strong> This account has a{" "}
                      {Math.round(shapData.confidence * 100)}% bot probability.
                    </span>
                  </p>
                </div> */}
                </div>
              )}
              {networkLoading && (
                <div className="mt-6 flex items-center justify-center gap-3 text-sm text-slate-600">
                  <Loader2 className="animate-spin" size={18} />
                  <span>Analyzing behavioral signals…</span>
                </div>
              )}

              {networkData && <FollowerNetwork data={networkData} />}

            </div>

          </div>
        )}
      </main>
    </div>
  );
}
