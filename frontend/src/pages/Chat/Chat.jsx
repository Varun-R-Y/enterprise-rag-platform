import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bot, FileWarning, ArrowRight, Menu } from 'lucide-react';

// UI Components
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Spinner from '../../components/ui/Spinner';
import Alert from '../../components/ui/Alert';

// Chat Components
import ChatWindow from '../../components/chat/ChatWindow';
import ChatInput from '../../components/chat/ChatInput';

// Conversation Sidebar & Modals
import ConversationSidebar from '../../components/conversation/ConversationSidebar';
import DeleteConversationModal from '../../components/conversation/DeleteConversationModal';
import EmptyConversationState from '../../components/conversation/EmptyConversationState';

// Services
import chatService from '../../services/chatService';
import documentService from '../../services/documentService';
import conversationService from '../../services/conversationService';
import PdfViewer from '../../components/pdf/PdfViewer';

export default function Chat() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialActiveId = location.state?.activeId || null;

  // Safeguard: Check if tenant has indexed documents
  const [checkingDocs, setCheckingDocs] = useState(true);
  const [hasDocs, setHasDocs] = useState(null); // null | true | false

  // Main UI/UX States
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(initialActiveId); // Set from redirect state if available
  const [messages, setMessages] = useState([]);
  const [activePdf, setActivePdf] = useState(null);
  const [inputText, setInputText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Mobile Sidebar Drawer
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Pagination States
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  // Deletion Modal States
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [convToDelete, setConvToDelete] = useState(null);
  const [deletingConv, setDeletingConv] = useState(false);

  // Status Banners
  const [alert, setAlert] = useState(null);

  // Ref to prevent race conditions during message history loading
  const activeLoadRef = useRef(null);
  const isNewConversationRef = useRef(false);

  // 1. Initial documents count verification
  const checkDocumentCount = async () => {
    setCheckingDocs(true);
    try {
      const docs = await documentService.getDocuments();
      setHasDocs(docs && docs.length > 0);
    } catch (err) {
      console.error('Failed to check documents count:', err);
      setAlert({
        type: 'error',
        message: 'Unable to verify document status. Please check backend connection.',
      });
      setHasDocs(false);
    } finally {
      setCheckingDocs(false);
    }
  };

  // 2. Fetch conversations list
  const loadConversationsList = async (pageNum = 1, append = false) => {
    if (pageNum === 1) {
      setPage(1);
    }
    try {
      if (append) {
        setLoadingMore(true);
      }
      const limit = 20;
      const list = await conversationService.getConversations(pageNum, limit);
      
      setConversations((prev) => {
        const merged = append ? [...prev, ...list] : list;
        // Eliminate duplicate entries by ID
        const unique = [];
        const seen = new Set();
        for (const c of merged) {
          if (!seen.has(c.id)) {
            seen.add(c.id);
            unique.push(c);
          }
        }
        return unique;
      });
      
      setHasMore(list.length === limit);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setAlert({
        type: 'error',
        message: 'Failed to retrieve conversation history. Please refresh the page.',
      });
    } finally {
      setLoadingMore(false);
    }
  };

  // 3. Load message history when activeId changes
  const loadActiveConversationHistory = async (convId) => {
    if (!convId) {
      setMessages([]);
      return;
    }

    setLoadingHistory(true);
    setAlert(null);
    activeLoadRef.current = convId;

    try {
      const history = await conversationService.getConversationMessages(convId);
      
      // Prevent updating state if the active conversation has shifted during network wait
      if (activeLoadRef.current !== convId) return;

      const formattedMessages = history.map((msg) => ({
        id: msg.id,
        text: msg.content,
        isUser: msg.role === 'user',
        timestamp: new Date(msg.created_at),
        sources: msg.citations || [],
      }));

      setMessages(formattedMessages);
    } catch (err) {
      console.error('Failed to load chat messages:', err);
      setAlert({
        type: 'error',
        message: 'Failed to retrieve conversation messages.',
      });
    } finally {
      if (activeLoadRef.current === convId) {
        setLoadingHistory(false);
      }
    }
  };

  useEffect(() => {
    checkDocumentCount();
  }, []);

  useEffect(() => {
    if (hasDocs) {
      loadConversationsList(1);
    }
  }, [hasDocs]);

  useEffect(() => {
    if (hasDocs) {
      if (isNewConversationRef.current) {
        isNewConversationRef.current = false;
      } else {
        loadActiveConversationHistory(activeId);
      }
    }
  }, [activeId, hasDocs]);

  // Load next paginated set of conversations
  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    loadConversationsList(nextPage, true);
  };

  // Trigger temporary "New Chat" empty view (does not hit the database)
  const handleCreateNewChat = () => {
    setActiveId(null);
    setMessages([]);
    setInputText('');
    setAlert(null);
  };

  // Switch selected conversation
  const handleSelectConversation = (conv) => {
    setActiveId(conv.id);
    setActivePdf(null); // Close PDF when switching chats
  };

  const handleSelectCitation = (documentId, filename, page) => {
    if (documentId) {
      setActivePdf({ documentId, filename, page });
    } else {
      console.warn('Citation is missing document_id:', filename);
      setAlert({
        type: 'error',
        message: `Could not load PDF document "${filename}" because its ID is missing.`,
      });
    }
  };

  // Open conversation deletion confirmation dialog
  const handleDeleteClick = (conv) => {
    setConvToDelete(conv);
    setDeleteModalOpen(true);
  };

  // Execute conversation deletion
  const handleDeleteConfirm = async () => {
    if (!convToDelete) return;
    setDeletingConv(true);
    setAlert(null);

    try {
      await conversationService.deleteConversation(convToDelete.id);
      
      // Remove from state
      setConversations((prev) => prev.filter((c) => c.id !== convToDelete.id));
      
      // Determine the next conversation to select automatically
      if (activeId === convToDelete.id) {
        const remaining = conversations.filter((c) => c.id !== convToDelete.id);
        if (remaining.length > 0) {
          // Select the next conversation in list
          setActiveId(remaining[0].id);
        } else {
          // No conversations remain
          setActiveId(null);
          setMessages([]);
        }
      }
      
      setDeleteModalOpen(false);
      setConvToDelete(null);
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setAlert({
        type: 'error',
        message: 'Failed to delete the conversation. Please try again.',
      });
    } finally {
      setDeletingConv(false);
    }
  };

  // Send message
  const handleSend = async (textToSend = inputText) => {
    const trimmedText = textToSend.trim();
    if (!trimmedText || isGenerating) return;

    let currentConvId = activeId;
    setAlert(null);

    // 1. Lazy creation: if no active conversation exists, create one first in the DB
    if (!currentConvId) {
      setIsGenerating(true);
      try {
        const titleText = trimmedText.length > 40 ? trimmedText.substring(0, 37) + '...' : trimmedText;
        isNewConversationRef.current = true;
        const newConv = await conversationService.createConversation(titleText);
        
        // Add to top of local conversations list
        setConversations((prev) => [newConv, ...prev]);
        setActiveId(newConv.id);
        currentConvId = newConv.id;
      } catch (err) {
        console.error('Failed to lazy create conversation:', err);
        setAlert({
          type: 'error',
          message: 'Failed to initialize a new conversation session. Please try again.',
        });
        setIsGenerating(false);
        return;
      }
    }

    // 2. Append local User message bubble immediately in screen
    const userMessage = {
      id: `user-${Date.now()}`,
      text: trimmedText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsGenerating(true);

    // 3. Query RAG backend with conversation ID
    try {
      const response = await chatService.askQuestion(trimmedText, currentConvId);
      
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        text: response.answer,
        isUser: false,
        timestamp: new Date(),
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // 4. Refresh conversations list to update titles and message counts
      loadConversationsList(1);
    } catch (err) {
      console.error('RAG generation failed:', err);
      let errorMsg = 'Failed to generate answer. Please try again.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setIsGenerating(false);
    }
  };

  // Regenerate last response by resending user prompt
  const handleRegenerate = async (promptText) => {
    if (isGenerating || !activeId || !promptText) return;

    setIsGenerating(true);
    setAlert(null);

    // Remove the last assistant message before regenerating
    setMessages((prev) => {
      const updated = [...prev];
      if (updated.length > 0 && !updated[updated.length - 1].isUser) {
        updated.pop();
      }
      return updated;
    });

    try {
      const response = await chatService.askQuestion(promptText, activeId);
      
      const newAssistantMessage = {
        id: `assistant-${Date.now()}`,
        text: response.answer,
        isUser: false,
        timestamp: new Date(),
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, newAssistantMessage]);
      loadConversationsList(1); // update counts
    } catch (err) {
      console.error('Regeneration failed:', err);
      let errorMsg = 'Failed to regenerate response. Please try again.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setIsGenerating(false);
    }
  };

  // Loading Document index count status on mount
  if (checkingDocs) {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-3">
        <Spinner size="lg" />
        <span className="text-sm font-semibold text-slate-500 animate-pulse">
          Loading AI conversational assistant...
        </span>
      </div>
    );
  }

  // Blocked state if no documents are uploaded for RAG
  if (!hasDocs) {
    return (
      <div className="max-w-md mx-auto my-12 animate-in fade-in duration-200">
        <Card className="flex flex-col items-center justify-center text-center p-8 bg-white border border-slate-200 shadow-sm rounded-xl">
          <div className="p-4 bg-amber-50 text-amber-600 rounded-full mb-4 border border-amber-100 shrink-0">
            <FileWarning size={32} />
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-2">No indexed documents found</h3>
          <p className="text-sm text-slate-500 mb-6 leading-relaxed">
            Retrieval-Augmented Generation requires reference files. Please upload at least one PDF document before starting a conversation.
          </p>
          <Button
            onClick={() => navigate('/documents')}
            variant="primary"
            className="w-full h-11 px-4 py-2 cursor-pointer flex items-center justify-center gap-2 font-semibold"
          >
            Go to Documents
            <ArrowRight size={16} />
          </Button>
        </Card>
      </div>
    );
  }

  // If the user has chats loaded, or they are in a temporary "New Chat" view:
  const isConversationsListEmpty = false;

  return (
    <div className="flex h-[calc(100vh-100px)] border border-slate-200 rounded-2xl overflow-hidden bg-slate-50 shadow-xs max-w-6xl mx-auto w-full">
      
      {/* 1. Sidebar Panel (persistent on desktop, overlay drawer on mobile) */}
      <ConversationSidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelectConversation}
        onDeleteClick={handleDeleteClick}
        onCreateNew={handleCreateNewChat}
        onLoadMore={handleLoadMore}
        hasMore={hasMore}
        loadingMore={loadingMore}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* 2. Main Chat Panel */}
      <div className="flex-grow flex flex-col min-w-0 bg-white">
        
        {/* Header toolbar */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-3 min-w-0">
            {/* Mobile Sidebar Hamburger Toggle */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 text-slate-500 hover:bg-slate-100 rounded-md transition md:hidden shrink-0 cursor-pointer focus:outline-none"
              aria-label="Open chat history sidebar"
            >
              <Menu size={20} />
            </button>
            <div className="min-w-0">
              <h1 className="text-md md:text-lg font-bold text-slate-900 truncate">
                {activeId ? (conversations.find((c) => c.id === activeId)?.title || 'Chat') : 'New Chat'}
              </h1>
              <p className="text-xs text-slate-500 mt-0.5 truncate hidden sm:block">
                Context-grounded AI knowledge helper
              </p>
            </div>
          </div>

          {/* Connected Model Badge */}
          <div className="flex items-center gap-2 p-1.5 px-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] font-bold shadow-3xs select-none">
            <span className="text-slate-400">Model:</span>
            <span className="text-slate-700">Phi-3 Mini</span>
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping shrink-0" />
            <span className="text-emerald-600">Connected</span>
          </div>
        </div>

        {/* Status banner */}
        {alert && (
          <div className="px-6 pt-3 shrink-0">
            <Alert
              type={alert.type}
              message={alert.message}
              onClose={() => setAlert(null)}
              className="animate-in fade-in slide-in-from-top-1 duration-200"
            />
          </div>
        )}

        {/* Content View */}
        <div className="flex-grow min-h-0 flex flex-col justify-between p-6">
          {isConversationsListEmpty ? (
            <EmptyConversationState onCreateNew={handleCreateNewChat} />
          ) : loadingHistory ? (
            <div className="flex-grow flex flex-col items-center justify-center gap-3">
              <Spinner size="md" />
              <span className="text-xs font-semibold text-slate-400 animate-pulse">
                Loading messages...
              </span>
            </div>
          ) : (
            <div className="flex-grow min-h-0 flex flex-col justify-between">
              <ChatWindow
                messages={messages}
                isGenerating={isGenerating}
                onSelectPrompt={handleSend}
                onRegenerate={handleRegenerate}
                onSelectCitation={handleSelectCitation}
              />
            </div>
          )}

          {/* Bottom input area */}
          {!isConversationsListEmpty && (
            <div className="shrink-0 pt-4 bg-white border-t border-slate-100">
              <ChatInput
                key={activeId || 'new'}
                value={inputText}
                onChange={setInputText}
                onSubmit={() => handleSend()}
                disabled={isGenerating || loadingHistory}
              />
              <p className="text-[10px] text-slate-400 text-center mt-2 font-medium">
                Assistant retrieves relevant context from your corporate database to ground answers.
              </p>
            </div>
          )}
        </div>

      </div>

      {/* 3. PDF Viewer split-view panel on desktop */}
      {activePdf && (
        <div className="hidden lg:block lg:w-[450px] xl:w-[550px] border-l border-slate-200 shrink-0 h-full relative">
          <PdfViewer
            documentId={activePdf.documentId}
            initialPage={activePdf.page}
            title={activePdf.filename}
            onClose={() => setActivePdf(null)}
          />
        </div>
      )}

      {/* 4. PDF Viewer overlay modal on mobile/tablet */}
      {activePdf && (
        <div className="lg:hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white w-full h-full rounded-xl overflow-hidden shadow-2xl flex flex-col">
            <PdfViewer
              documentId={activePdf.documentId}
              initialPage={activePdf.page}
              title={activePdf.filename}
              onClose={() => setActivePdf(null)}
            />
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      <DeleteConversationModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setConvToDelete(null);
        }}
        onConfirm={handleDeleteConfirm}
        deleting={deletingConv}
        conversationTitle={convToDelete?.title || ''}
      />

    </div>
  );
}
