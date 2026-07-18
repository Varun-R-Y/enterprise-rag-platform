import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  UploadCloud,
  FileText,
  Scissors,
  Cpu,
  Database,
  MessageSquare,
  ShieldCheck,
  Users,
  Layers,
  Search,
  MessageCircle,
  FileJson,
  Lock,
  ArrowDown
} from 'lucide-react';

// UI Components
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Container from '../../components/ui/Container';
import Section from '../../components/ui/Section';
import SectionHeading from '../../components/ui/SectionHeading';
import FeatureCard from '../../components/ui/FeatureCard';
import TechBadge from '../../components/ui/TechBadge';

export default function Landing() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleCTA = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
  };

  return (
    <div className="bg-slate-50 min-h-screen flex flex-col font-sans">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-slate-200 h-16 flex items-center">
        <Container className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="text-indigo-600" size={24} />
            <span className="font-bold text-lg text-slate-900 tracking-wide">Enterprise RAG</span>
          </div>
          
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Features</a>
            <a href="#pipeline" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Pipeline</a>
            <a href="#techstack" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Tech Stack</a>
            <a href="#architecture" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Architecture</a>
          </nav>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <Button onClick={() => navigate('/dashboard')} variant="primary" className="h-10 px-4 text-sm py-1.5">
                Dashboard
              </Button>
            ) : (
              <>
                <Button onClick={() => navigate('/login')} variant="secondary" className="h-10 px-4 text-sm py-1.5 border-none shadow-none text-indigo-600 hover:text-indigo-700">
                  Sign In
                </Button>
                <Button onClick={() => navigate('/register')} variant="primary" className="h-10 px-4 text-sm py-1.5">
                  Get Started
                </Button>
              </>
            )}
          </div>
        </Container>
      </header>

      {/* Hero Section */}
      <Section bg="light" className="flex items-center pt-24 pb-16">
        <Container className="text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1] max-w-4xl mx-auto mb-6">
            Enterprise-Grade Document Intelligence & <span className="text-indigo-600">Semantic RAG</span>
          </h1>
          <p className="text-slate-600 text-base md:text-lg leading-[1.6] max-w-2xl mx-auto mb-8">
            A production-ready retrieval-augmented generation platform. Upload corporate documents, chunk them semantically, and obtain context-aware LLM answers.
          </p>
          <div className="flex justify-center items-center">
            <Button onClick={handleCTA} variant="primary" className="w-full sm:w-auto px-12">
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
            </Button>
          </div>
        </Container>
      </Section>

      {/* Trusted Tech Grid */}
      <Section bg="gray" className="py-12 border-y border-slate-200">
        <Container className="text-center">
          <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider block mb-6">Powered by Trusted Technologies</span>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-75">
            <span className="text-slate-800 font-bold text-lg">React</span>
            <span className="text-slate-800 font-bold text-lg">FastAPI</span>
            <span className="text-slate-800 font-bold text-lg">Ollama</span>
            <span className="text-slate-800 font-bold text-lg">Qdrant</span>
            <span className="text-slate-800 font-bold text-lg">PostgreSQL</span>
            <span className="text-slate-800 font-bold text-lg">Tailwind CSS</span>
          </div>
        </Container>
      </Section>

      {/* Problem We Solve */}
      <Section bg="light" id="problem">
        <Container>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider block mb-2">The Knowledge retrieval gap</span>
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-6 leading-tight">
                Enterprise knowledge is scattered. Keyword search fails.
              </h2>
              <p className="text-slate-600 text-base leading-[1.6] mb-4">
                Internal documentation, policies, employee manuals, and onboarding logs are typically trapped inside unstructured PDFs. Traditional keyword indexing searches for literal letter matches, yielding poor, context-less results.
              </p>
              <p className="text-slate-600 text-base leading-[1.6]">
                Our platform bridges this gap by reading document structures, splitting text logically via semantic boundary definitions, storing high-dimensional vector embeddings, and retrieving grounded context to local LLMs.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <Card>
                <h4 className="font-bold text-slate-900 mb-2">Traditional Search</h4>
                <p className="text-slate-500 text-sm leading-[1.5]">Returns files containing matching words. Ignores context, synonyms, and conceptual intent.</p>
              </Card>
              <Card className="border-indigo-600 ring-1 ring-indigo-600">
                <h4 className="font-bold text-indigo-600 mb-2">Semantic RAG</h4>
                <p className="text-slate-600 text-sm leading-[1.5]">Retrieves passages matching the query intent, grounding AI responses with certified sources.</p>
              </Card>
            </div>
          </div>
        </Container>
      </Section>

      {/* How It Works Pipeline */}
      <Section bg="gray" id="pipeline">
        <Container>
          <SectionHeading
            title="How It Works"
            subtitle="A modular pipeline that ingests raw documents and exposes a context-grounded interface."
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 relative">
            {/* Step 1 */}
            <Card className="relative flex flex-col justify-between">
              <div>
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-4"><UploadCloud size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">01. Ingestion</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Upload PDFs</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Secure document ingestion with multi-tenant storage mapping.</p>
              </div>
            </Card>

            {/* Step 2 */}
            <Card className="relative flex flex-col justify-between">
              <div>
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-4"><FileText size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">02. Extraction</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Extract Text</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Layout parsing to extract raw text blocks and metadata from documents.</p>
              </div>
            </Card>

            {/* Step 3 */}
            <Card className="relative flex flex-col justify-between">
              <div>
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-4"><Scissors size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">03. Partitioning</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Semantic Chunking</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Logical document splitting based on semantic boundaries rather than fixed characters.</p>
              </div>
            </Card>

            {/* Step 4 */}
            <Card className="relative flex flex-col justify-between">
              <div>
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-4"><Cpu size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">04. Representation</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Generate Embeddings</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Run local Sentence Transformers to translate text chunks into dense vector representations.</p>
              </div>
            </Card>

            {/* Step 5 */}
            <Card className="relative flex flex-col justify-between">
              <div>
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-4"><Database size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">05. Storage</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Store in Qdrant</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Index embedding vectors in Qdrant with payload parameters for filtered search.</p>
              </div>
            </Card>

            {/* Step 6 */}
            <Card className="relative flex flex-col justify-between border-indigo-600 ring-1 ring-indigo-600">
              <div>
                <div className="p-3 bg-indigo-600 text-white rounded-lg w-fit mb-4"><MessageSquare size={24} /></div>
                <span className="text-indigo-600 font-bold text-sm tracking-wide block mb-1">06. Generation</span>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">AI Chat Response</h3>
                <p className="text-slate-500 text-sm leading-relaxed">Retrieve context, compile grounding prompts, and generate local Ollama LLM chat responses.</p>
              </div>
            </Card>
          </div>
        </Container>
      </Section>

      {/* Platform Features */}
      <Section bg="light" id="features">
        <Container>
          <SectionHeading
            title="Platform Capabilities"
            subtitle="Explore the standard feature set built into the enterprise portal."
          />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={Lock}
              title="JWT Authentication"
              description="Stateless token storage and session control with request interceptors."
            />
            <FeatureCard
              icon={Users}
              title="Multi-Tenant Isolation"
              description="Strict database schema and vector namespace partitioning for tenants."
            />
            <FeatureCard
              icon={UploadCloud}
              title="Background Indexing"
              description="Offloaded out-of-band processing queue for PDF layout extractions."
            />
            <FeatureCard
              icon={Search}
              title="Vector Search"
              description="High-speed cosine similarities indexing on Qdrant collections."
            />
            <FeatureCard
              icon={MessageCircle}
              title="AI Generation"
              description="Context grounding LLM prompt assembly using local Ollama model endpoints."
            />
            <FeatureCard
              icon={FileJson}
              title="Conversation Logs"
              description="Session history schemas mapping user queries and model completions."
            />
            <FeatureCard
              icon={Scissors}
              title="Semantic Chunking"
              description="Sentence transformers and text splitters optimized for structural docs."
            />
            <FeatureCard
              icon={ShieldCheck}
              title="Enterprise Security"
              description="Decoupled authentication guard layers and backend CORS controllers."
            />
          </div>
        </Container>
      </Section>

      {/* Tech Stack Grid */}
      <Section bg="gray" id="techstack">
        <Container>
          <SectionHeading
            title="System Technology Matrix"
            subtitle="The production technologies powering each layer of the platform."
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            <TechBadge category="Frontend" items={['React 19', 'Vite', 'Tailwind CSS v4', 'React Router 7']} />
            <TechBadge category="Backend" items={['FastAPI', 'Uvicorn', 'SQLAlchemy', 'Pydantic v2']} />
            <TechBadge category="AI & Embeddings" items={['Ollama', 'Sentence Transformers', 'LangChain (Core)']} />
            <TechBadge category="Databases" items={['Qdrant (Vector)', 'PostgreSQL', 'SQLite (Dev)']} />
            <TechBadge category="Infrastructure" items={['JWT Auth', 'Docker-Ready', 'Python Logging']} />
          </div>
        </Container>
      </Section>

      {/* Architecture Diagram */}
      <Section bg="light" id="architecture">
        <Container>
          <SectionHeading
            title="System Architecture Flow"
            subtitle="Decoupled full-stack communication loop layout."
          />
          <div className="max-w-4xl mx-auto flex flex-col items-center gap-4">
            
            {/* React Frontend */}
            <Card className="w-full max-w-lg text-center border-indigo-200">
              <h4 className="font-bold text-indigo-600 text-lg">React Frontend UI</h4>
              <p className="text-slate-500 text-xs mt-1">Vite • Axios Interceptors • React Router DOM</p>
            </Card>

            <ArrowDown className="text-indigo-500" size={24} />

            {/* FastAPI API Gateway */}
            <Card className="w-full max-w-lg text-center border-indigo-200">
              <h4 className="font-bold text-indigo-600 text-lg">FastAPI Gateway / Core Backend</h4>
              <p className="text-slate-500 text-xs mt-1">Uvicorn Server • CORS Middlewares • Router Handlers</p>
            </Card>

            <ArrowDown className="text-indigo-500" size={24} />

            {/* Middle Services Layer */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
              {/* Relational DB */}
              <Card className="text-center bg-slate-50 border-slate-200">
                <h5 className="font-semibold text-slate-800">PostgreSQL / SQLite</h5>
                <p className="text-slate-500 text-xs mt-2">Users, Tenants, Document Meta & Conversational History Records</p>
              </Card>

              {/* Vector Database */}
              <Card className="text-center bg-slate-50 border-slate-200">
                <h5 className="font-semibold text-slate-800">Qdrant Vector DB</h5>
                <p className="text-slate-500 text-xs mt-2">Collection Management, High-Dimensional Vector Embeddings, payload searches</p>
              </Card>

              {/* Local LLM */}
              <Card className="text-center bg-slate-50 border-slate-200">
                <h5 className="font-semibold text-slate-800">Ollama Local LLM</h5>
                <p className="text-slate-500 text-xs mt-2">Sentence Embeddings Extraction & Generative Retrieval Grounding</p>
              </Card>
            </div>

          </div>
        </Container>
      </Section>

      {/* Call to Action */}
      <Section bg="gray" className="py-24">
        <Container className="text-center max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-6">
            Ready to explore the document workspace?
          </h2>
          <p className="text-slate-600 mb-8 max-w-xl mx-auto">
            Set up an account under the default tenant and test the pipeline, indexing, and chat functions.
          </p>
          <div className="flex justify-center items-center">
            <Button onClick={handleCTA} variant="primary" className="w-full sm:w-auto px-12">
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
            </Button>
          </div>
        </Container>
      </Section>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-12 text-slate-500 text-sm">
        <Container className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Layers className="text-indigo-600" size={20} />
            <span className="font-semibold text-slate-700 tracking-wide">Enterprise RAG Platform</span>
          </div>
          <div>
            <span>&copy; {new Date().getFullYear()} Enterprise RAG Platform. All rights reserved.</span>
          </div>
          <div className="flex gap-6">
            <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noopener noreferrer" className="hover:text-slate-800 transition">FastAPI Docs</a>
            <a href="https://qdrant.tech/" target="_blank" rel="noopener noreferrer" className="hover:text-slate-800 transition">Qdrant Docs</a>
          </div>
        </Container>
      </footer>
    </div>
  );
}
