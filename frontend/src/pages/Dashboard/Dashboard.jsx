import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  MessageSquare, 
  Zap, 
  UploadCloud, 
  ArrowRight, 
  Clock, 
  Database, 
  Sparkles,
  BookOpen,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import documentService from '../../services/documentService';
import conversationService from '../../services/conversationService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Spinner from '../../components/ui/Spinner';
import Alert from '../../components/ui/Alert';
import Badge from '../../components/ui/Badge';

export default function Dashboard() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  // State Management
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch metrics data on mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [docs, convs] = await Promise.all([
          documentService.getDocuments(),
          conversationService.getConversations(1, 5) // Fetch recent conversations
        ]);
        setDocuments(docs || []);
        setConversations(convs || []);
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
        setError('Failed to load metrics. Please verify backend connection.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Format Helper Functions
  const formatBytes = (bytes, decimals = 1) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  // Metrics calculations
  const totalDocs = documents.length;
  const completedDocs = documents.filter(d => d.status === 'COMPLETED').length;
  const processingDocs = documents.filter(d => d.status === 'PROCESSING' || d.status === 'PENDING').length;
  const failedDocs = documents.filter(d => d.status === 'FAILED').length;
  
  const totalChats = conversations.length;
  const totalTurns = conversations.reduce((acc, c) => acc + (c.message_count || 0), 0);

  // Render Loading Spinner
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-3">
        <Spinner size="lg" />
        <span className="text-sm font-semibold text-slate-500 animate-pulse">
          Loading metrics and workspace status...
        </span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300">
      
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 md:p-8 rounded-2xl border border-indigo-950/40 text-white shadow-sm relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.15),transparent_40%)]" />
        <div className="space-y-1 relative z-10">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">
            Welcome back, {currentUser?.full_name || 'User'}!
          </h1>
          <p className="text-xs md:text-sm text-slate-300 leading-relaxed max-w-xl">
            This is your workspace dashboard. Manage uploaded manuals, monitor ingestion pipelines, and query your secure knowledge base.
          </p>
        </div>
        <div className="flex items-center gap-2 p-2 px-4 bg-white/10 backdrop-blur-md rounded-xl text-xs font-semibold self-start md:self-auto relative z-10 select-none border border-white/5">
          <Calendar size={14} className="text-indigo-300" />
          <span>{new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</span>
        </div>
      </div>

      {error && (
        <Alert type="error" message={error} onClose={() => setError(null)} />
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Metric 1: Documents */}
        <Card className="hover:shadow-md transition duration-200">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Documents Ingested</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-800">{completedDocs}</span>
                {totalDocs > completedDocs && (
                  <span className="text-xs font-semibold text-slate-500">/ {totalDocs} total</span>
                )}
              </div>
              
              {/* Mini Status Breakdown bar */}
              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex mt-2">
                <div 
                  className="bg-emerald-500 h-full transition-all duration-500" 
                  style={{ width: `${totalDocs ? (completedDocs / totalDocs) * 100 : 0}%` }}
                />
                <div 
                  className="bg-amber-400 h-full transition-all duration-500" 
                  style={{ width: `${totalDocs ? (processingDocs / totalDocs) * 100 : 0}%` }}
                />
                <div 
                  className="bg-red-500 h-full transition-all duration-500" 
                  style={{ width: `${totalDocs ? (failedDocs / totalDocs) * 100 : 0}%` }}
                />
              </div>
              <div className="flex items-center gap-3 text-[10px] font-bold text-slate-400 pt-1">
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" /> {completedDocs} Ok</span>
                {processingDocs > 0 && <span className="flex items-center gap-1 animate-pulse"><span className="w-1.5 h-1.5 bg-amber-400 rounded-full" /> {processingDocs} Ingestion</span>}
                {failedDocs > 0 && <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-red-500 rounded-full" /> {failedDocs} Fail</span>}
              </div>
            </div>
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <FileText size={20} />
            </div>
          </div>
        </Card>

        {/* Metric 2: Conversations */}
        <Card className="hover:shadow-md transition duration-200">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Chat Sessions</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-800">{totalChats}</span>
                <span className="text-xs font-medium text-slate-500">active threads</span>
              </div>
              <p className="text-xs text-slate-400 leading-normal">
                Ask questions scoped strictly to your isolated company documents.
              </p>
            </div>
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <MessageSquare size={20} />
            </div>
          </div>
        </Card>

        {/* Metric 3: Total Interaction Turns */}
        <Card className="hover:shadow-md transition duration-200">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Interactions</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-800">{totalTurns}</span>
                <span className="text-xs font-medium text-slate-500">message turns</span>
              </div>
              <p className="text-xs text-slate-400 leading-normal">
                Exchanged with local LLM Phi-3 Mini using semantic citations.
              </p>
            </div>
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <Zap size={20} />
            </div>
          </div>
        </Card>

      </div>

      {/* Main Details Section: Documents & Chats split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Side: Recent Documents */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-slate-800 text-lg">
              <Database size={18} className="text-indigo-600" />
              <h2>Knowledge Base Status</h2>
            </div>
            <Button 
              onClick={() => navigate('/documents')} 
              variant="secondary"
              className="text-xs px-3 py-1.5 font-semibold flex items-center gap-1.5 h-8 cursor-pointer"
            >
              Manage
              <ArrowRight size={12} />
            </Button>
          </div>

          <Card className="p-0 overflow-hidden border border-slate-200">
            {documents.length === 0 ? (
              <div className="p-8 text-center space-y-4">
                <div className="p-3 bg-slate-50 text-slate-400 rounded-full w-12 h-12 mx-auto flex items-center justify-center border border-slate-100">
                  <UploadCloud size={24} />
                </div>
                <h3 className="font-bold text-slate-700 text-sm">No documents uploaded yet</h3>
                <p className="text-xs text-slate-400 max-w-xs mx-auto">
                  Upload PDF files to start generating vector chunks for retrieval-grounded AI search.
                </p>
                {currentUser?.role === 'ADMIN' && (
                  <Button 
                    onClick={() => navigate('/documents')} 
                    variant="primary" 
                    className="text-xs px-4 py-2 cursor-pointer font-semibold"
                  >
                    Upload PDF
                  </Button>
                )}
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {documents.slice(0, 3).map((doc) => (
                  <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="p-2 bg-indigo-50/50 text-indigo-500 rounded-lg border border-indigo-100 shrink-0">
                        <FileText size={16} />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-slate-800 truncate" title={doc.original_filename}>
                          {doc.original_filename}
                        </h4>
                        <div className="flex items-center gap-2 text-[10px] text-slate-400 font-medium mt-0.5">
                          <span>{formatBytes(doc.file_size)}</span>
                          <span>•</span>
                          <span>{formatDate(doc.uploaded_at)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div>
                      {doc.status === 'COMPLETED' && (
                        <Badge variant="success">Completed</Badge>
                      )}
                      {(doc.status === 'PROCESSING' || doc.status === 'PENDING') && (
                        <Badge variant="primary" className="animate-pulse bg-amber-50 text-amber-600 border border-amber-200">
                          Processing
                        </Badge>
                      )}
                      {doc.status === 'FAILED' && (
                        <Badge variant="primary" className="bg-red-50 text-red-600 border border-red-200">
                          Failed
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Side: Recent Chats */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-slate-800 text-lg">
              <MessageSquare size={18} className="text-indigo-600" />
              <h2>Recent Conversations</h2>
            </div>
            <Button 
              onClick={() => navigate('/chat')} 
              variant="secondary"
              className="text-xs px-3 py-1.5 font-semibold flex items-center gap-1.5 h-8 cursor-pointer"
            >
              All Chats
              <ArrowRight size={12} />
            </Button>
          </div>

          <Card className="p-0 overflow-hidden border border-slate-200">
            {conversations.length === 0 ? (
              <div className="p-8 text-center space-y-4">
                <div className="p-3 bg-slate-50 text-slate-400 rounded-full w-12 h-12 mx-auto flex items-center justify-center border border-slate-100">
                  <MessageSquare size={24} />
                </div>
                <h3 className="font-bold text-slate-700 text-sm">No conversations recorded</h3>
                <p className="text-xs text-slate-400 max-w-xs mx-auto">
                  Once you upload a document, launch a chat session to interrogate your context.
                </p>
                <Button 
                  onClick={() => navigate('/chat')} 
                  variant="primary" 
                  className="text-xs px-4 py-2 cursor-pointer font-semibold"
                  disabled={!completedDocs}
                >
                  Start New Chat
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {conversations.slice(0, 3).map((conv) => (
                  <div key={conv.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="p-2 bg-indigo-50/50 text-indigo-500 rounded-lg border border-indigo-100 shrink-0">
                        <MessageSquare size={16} />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-slate-800 truncate" title={conv.title}>
                          {conv.title}
                        </h4>
                        <div className="flex items-center gap-2 text-[10px] text-slate-400 font-medium mt-0.5">
                          <span>{conv.message_count || 0} messages</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Clock size={10} />
                            {formatDate(conv.updated_at)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Resume Chat Button */}
                    <button
                      onClick={() => navigate('/chat', { state: { activeId: conv.id } })}
                      className="text-xs font-bold text-indigo-600 hover:text-indigo-800 cursor-pointer flex items-center gap-1 hover:underline transition focus:outline-none"
                    >
                      Resume
                      <ArrowRight size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

      </div>

      {/* RAG Workflow Steps Banner */}
      <div className="space-y-4 pt-4 border-t border-slate-200">
        <div className="flex items-center gap-2 font-bold text-slate-800 text-lg">
          <BookOpen size={18} className="text-indigo-600" />
          <h2>How Enterprise RAG Works</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-slate-50/50 hover:bg-white transition border border-slate-200 p-5 rounded-2xl">
            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center border border-indigo-100 text-indigo-600 mb-4 shadow-3xs shrink-0 select-none">
              <UploadCloud size={18} />
            </div>
            <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider mb-2">1. Ingest Documents</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Upload PDF manuals, policies, or contracts. Files are securely partitioned and saved under your tenant directory.
            </p>
          </Card>
          
          <Card className="bg-slate-50/50 hover:bg-white transition border border-slate-200 p-5 rounded-2xl">
            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center border border-indigo-100 text-indigo-600 mb-4 shadow-3xs shrink-0 select-none">
              <Database size={18} />
            </div>
            <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider mb-2">2. Chunk & Embed</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              The pipeline parses pages, splits content into overlapping segments, generates embeddings using BGE Small, and stores them in Qdrant.
            </p>
          </Card>

          <Card className="bg-slate-50/50 hover:bg-white transition border border-slate-200 p-5 rounded-2xl">
            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center border border-indigo-100 text-indigo-600 mb-4 shadow-3xs shrink-0 select-none">
              <Sparkles size={18} />
            </div>
            <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider mb-2">3. Context Chat</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Submit questions. The assistant retrieves relevant segments matching your tenant, formulates a grounded prompt, and queries Phi-3 Mini.
            </p>
          </Card>
        </div>
      </div>

    </div>
  );
}
