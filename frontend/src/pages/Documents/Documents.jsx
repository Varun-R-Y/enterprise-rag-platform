import { useState, useEffect } from 'react';
import { RefreshCw, Search, UploadCloud, Plus, SlidersHorizontal, Layers, CheckCircle2, AlertTriangle, FileText, Loader2 } from 'lucide-react';

// UI Components
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Spinner from '../../components/ui/Spinner';
import Modal from '../../components/ui/Modal';
import Alert from '../../components/ui/Alert';
import EmptyState from '../../components/ui/EmptyState';

// Document Components
import UploadZone from '../../components/document/UploadZone';
import UploadProgress from '../../components/document/UploadProgress';
import DocumentTable from '../../components/document/DocumentTable';
import DeleteConfirmation from '../../components/document/DeleteConfirmation';

// Services
import documentService from '../../services/documentService';
import { useAuth } from '../../contexts/AuthContext';

export default function Documents() {
  const { currentUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  
  // Upload Queue State
  const [uploadingFiles, setUploadingFiles] = useState([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Deletion Modal State
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Alert State
  const [alert, setAlert] = useState(null);

  // Stats calculation
  const totalCount = documents.length;
  const completedCount = documents.filter((d) => d.status?.toLowerCase() === 'completed').length;
  const processingCount = documents.filter((d) => ['pending', 'processing'].includes(d.status?.toLowerCase())).length;
  const failedCount = documents.filter((d) => d.status?.toLowerCase() === 'failed').length;

  // Fetch documents from backend
  const fetchDocuments = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    else setRefreshing(true);
    
    try {
      const data = await documentService.getDocuments();
      setDocuments(data || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      let errorMsg = 'Could not retrieve documents. Please check backend connection.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchDocuments(false);
  }, []);

  // Smart status polling
  useEffect(() => {
    const hasActiveJobs = documents.some((d) =>
      ['pending', 'processing'].includes(d.status?.toLowerCase())
    );

    if (!hasActiveJobs) return;

    const interval = setInterval(() => {
      fetchDocuments(true);
    }, 5000);

    return () => clearInterval(interval);
  }, [documents]);

  // Handle file select & concurrent upload queue
  const handleFilesSelect = (files) => {
    const newQueueEntries = files.map((file) => ({
      id: `${file.name}-${Date.now()}`,
      name: file.name,
      fileObj: file,
      progress: 0,
      status: 'uploading',
      error: null,
    }));

    setUploadingFiles((prev) => [...newQueueEntries, ...prev]);

    newQueueEntries.forEach(async (entry) => {
      try {
        await documentService.uploadDocument(entry.fileObj, (percent) => {
          setUploadingFiles((prev) =>
            prev.map((f) => (f.id === entry.id ? { ...f, progress: percent } : f))
          );
        });

        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === entry.id ? { ...f, status: 'completed', progress: 100 } : f
          )
        );
        
        // Refresh document list silently
        fetchDocuments(true);
      } catch (err) {
        console.error('File upload failed:', err);
        let errorMsg = 'Upload failed.';
        if (err.response && err.response.data && err.response.data.detail) {
          errorMsg = typeof err.response.data.detail === 'string'
            ? err.response.data.detail
            : err.response.data.detail.map(e => e.msg).join(', ');
        }

        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === entry.id ? { ...f, status: 'failed', error: errorMsg } : f
          )
        );

        setAlert({
          type: 'error',
          message: `Failed to upload "${entry.name}": ${errorMsg}`,
        });
      }
    });
  };

  // Clear completed items from upload queue
  const handleClearQueue = () => {
    setUploadingFiles((prev) => prev.filter((f) => f.status === 'uploading'));
  };

  // Handle delete document action
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await documentService.deleteDocument(deleteTarget.id);
      setAlert({
        type: 'success',
        message: `Successfully deleted document "${deleteTarget.original_filename}"`,
      });
      setDeleteTarget(null);
      fetchDocuments(true);
    } catch (err) {
      console.error('Failed to delete document:', err);
      let errorMsg = 'Could not delete the document.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setIsDeleting(false);
    }
  };

  const showClearQueueBtn = uploadingFiles.some((f) => f.status !== 'uploading');

  return (
    <div className="space-y-6">
      {/* Notifications Alert Banner */}
      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
          className="animate-in fade-in slide-in-from-top-2 duration-200"
        />
      )}

      {/* Statistics Header Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">
            Total Documents
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{totalCount}</div>
        </Card>
        
        <Card className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-emerald-500 text-xs font-bold uppercase tracking-wider flex items-center gap-1">
            <CheckCircle2 size={14} />
            Indexed
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{completedCount}</div>
        </Card>
        
        <Card className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-indigo-500 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <RefreshCw size={12} className={processingCount > 0 ? 'animate-spin' : ''} />
            Processing
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{processingCount}</div>
        </Card>
        
        <Card className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-rose-500 text-xs font-bold uppercase tracking-wider flex items-center gap-1">
            <AlertTriangle size={14} />
            Failed
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{failedCount}</div>
        </Card>
      </div>

      {/* Main Title & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Documents</h1>
          <p className="text-slate-500 text-sm mt-1 leading-relaxed">
            Upload and manage PDF documents for multi-tenant semantic RAG indexing.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            onClick={() => fetchDocuments(true)}
            variant="secondary"
            className="h-10 px-3 cursor-pointer shrink-0"
            disabled={loading || refreshing}
            title="Refresh list"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin text-indigo-600' : 'text-slate-500'} />
          </Button>
          
          {currentUser?.role === 'ADMIN' && (
            <Button
              onClick={() => setIsUploadOpen(!isUploadOpen)}
              variant={isUploadOpen ? 'secondary' : 'primary'}
              className="h-10 px-4 py-2 cursor-pointer font-semibold flex items-center gap-2"
            >
              {isUploadOpen ? 'Close Upload' : 'Upload Document'}
              {!isUploadOpen && <Plus size={18} />}
            </Button>
          )}
        </div>
      </div>

      {/* Upload Zone & Queue List Container */}
      {isUploadOpen && currentUser?.role === 'ADMIN' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-top-4 duration-200">
          <div className="lg:col-span-2">
            <UploadZone
              onFilesSelect={handleFilesSelect}
              onError={(msg) => setAlert({ type: 'error', message: msg })}
            />
          </div>
          <div className="flex flex-col justify-start">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Progress Status
              </span>
              {showClearQueueBtn && (
                <button
                  onClick={handleClearQueue}
                  className="text-xs text-indigo-600 hover:text-indigo-500 font-bold focus:outline-none cursor-pointer"
                >
                  Clear Queue
                </button>
              )}
            </div>
            
            {uploadingFiles.length > 0 ? (
              <UploadProgress uploadingFiles={uploadingFiles} />
            ) : (
              <div className="flex flex-col items-center justify-center p-6 border border-dashed border-slate-200 rounded-xl bg-white text-center h-full min-h-[140px] text-slate-400 text-xs">
                <FileText size={20} className="mb-2 text-slate-300" />
                No uploads in progress.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Filter, Sort, & Data list Container */}
      <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 border-b border-slate-100 pb-5">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search documents by filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-slate-700 bg-white"
            />
          </div>

          {/* Sort selection drop down */}
          <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
            <SlidersHorizontal size={14} className="text-slate-400" />
            <label htmlFor="sort-select" className="text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0">
              Sort By:
            </label>
            <select
              id="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-slate-300 rounded-lg text-sm px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 bg-white font-medium cursor-pointer"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="name-az">File Name (A-Z)</option>
              <option value="name-za">File Name (Z-A)</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>

        {/* Loading Spinner */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <Spinner size="lg" />
            <span className="text-sm font-semibold text-slate-500 animate-pulse">
              Retrieving indexed repository...
            </span>
          </div>
        ) : totalCount === 0 ? (
          /* Workflow empty state */
          <EmptyState
            title="No documents uploaded yet"
            description={
              currentUser?.role === 'ADMIN'
                ? "Upload your corporate manuals, policy logs, or onboarding guidelines to begin multi-tenant semantic search indexing."
                : "No corporate manuals or policy logs have been indexed by your administrator yet."
            }
            actionLabel={currentUser?.role === 'ADMIN' ? "Upload First PDF" : null}
            onAction={currentUser?.role === 'ADMIN' ? () => setIsUploadOpen(true) : null}
          />
        ) : (
          /* Table / Cards list */
          <DocumentTable
            documents={documents}
            searchTerm={searchTerm}
            sortBy={sortBy}
            onDeleteClick={(doc) => setDeleteTarget(doc)}
            onRetryClick={() => {}} // Disabled retry placeholder click
            isAdmin={currentUser?.role === 'ADMIN'}
          />
        )}
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        title="Delete Document Confirmation"
      >
        {deleteTarget && (
          <DeleteConfirmation
            filename={deleteTarget.original_filename}
            onCancel={() => setDeleteTarget(null)}
            onConfirm={handleDeleteConfirm}
            isDeleting={isDeleting}
          />
        )}
      </Modal>
    </div>
  );
}
