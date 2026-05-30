import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import InstituteBrand from '../components/layout/InstituteBrand';
import {
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Code2,
  Trophy,
  Users,
  Clock,
  ArrowRight,
} from 'lucide-react';

const FEATURES = [
  {
    icon: ShieldCheck,
    title: 'Secure & Proctored',
    desc: 'Fullscreen monitoring, tab-switch detection and JWT authentication keep every exam fair.',
  },
  {
    icon: Code2,
    title: 'Built for Coders',
    desc: 'In-browser Monaco editor with Python, SQL & PySpark support and hidden test cases.',
  },
  {
    icon: Sparkles,
    title: 'AI Code Assistant',
    desc: 'Convert SQL → Spark SQL / PySpark instantly with our Databricks Llama-4 powered assistant.',
  },
  {
    icon: Clock,
    title: 'Auto-Evaluated MCQs',
    desc: 'Objective answers are graded the moment students hit submit. Descriptive answers are reviewed by you.',
  },
  {
    icon: Trophy,
    title: 'Leaderboards & Reports',
    desc: 'Track student performance with leaderboards, CSV/Excel/PDF exports and visual analytics.',
  },
  {
    icon: Users,
    title: 'Role-Based Access',
    desc: 'Super-admin, teacher and student dashboards with carefully scoped permissions.',
  },
];

const COURSES = [
  'Python', 'PySpark', 'SQL', 'Azure Databricks', 'SQL Server',
  'Azure Data Factory', 'Microsoft Fabric', 'Azure Synapse Analytics',
  'Azure Data Lake Gen2', 'Azure Event Hubs', 'Spark Streaming',
  'Data Engineering', 'Architect Designing', 'DSA', 'Java',
];

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-primary-50/40 to-white">
      <header className="sticky top-0 z-30 backdrop-blur bg-white/70 border-b border-slate-200">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          <InstituteBrand />
          <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-slate-600">
            <a href="#features" className="px-3 py-2 hover:text-slate-900">Features</a>
            <a href="#courses" className="px-3 py-2 hover:text-slate-900">Courses</a>
            <a href="#faq" className="px-3 py-2 hover:text-slate-900">FAQ</a>
          </nav>
          <div className="flex items-center gap-2">
            {user ? (
              <>
                <span className="hidden sm:inline text-sm text-slate-600 mr-1">
                  Hi, {user.first_name || user.email}
                </span>
                <Link to="/dashboard" className="btn-primary">Go to Dashboard</Link>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-secondary">Login</Link>
                <Link to="/register" className="btn-primary">Get started</Link>
              </>
            )}
          </div>
        </div>
      </header>

      {user && (
        <div className="bg-primary-600 text-white">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-2 text-sm">
            <p>You are signed in as <strong className="capitalize">{user.role?.replace('_', ' ')}</strong>.</p>
            <div className="flex flex-wrap gap-2">
              <Link to="/dashboard" className="rounded-lg bg-white/20 px-3 py-1 hover:bg-white/30">
                Dashboard
              </Link>
              <Link to="/exams" className="rounded-lg bg-white/20 px-3 py-1 hover:bg-white/30">
                Exams
              </Link>
              <Link to="/profile" className="rounded-lg bg-white/20 px-3 py-1 hover:bg-white/30">
                Profile
              </Link>
            </div>
          </div>
        </div>
      )}

      <section className="mx-auto max-w-7xl px-4 sm:px-6 py-16 lg:py-24">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div className="animate-slide-up">
            <span className="badge-primary">Free for all students • NGO initiative</span>
            <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Learn data engineering. <br />
              <span className="bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
                Prove it on every exam.
              </span>
            </h1>
            <p className="mt-5 text-lg text-slate-600 leading-relaxed">
              The official online examination platform of Mewati Institute of Technology.
              Auto-graded MCQs, descriptive answer evaluation, sandboxed coding tests and
              an AI code assistant - all in one place.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary">
                Start as a student <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/register" className="btn-secondary">
                I'm a teacher
              </Link>
            </div>
            <div className="mt-8 grid grid-cols-3 gap-4 max-w-md">
              <Stat label="Subjects" value="15+" />
              <Stat label="Question Types" value="6" />
              <Stat label="Free" value="100%" />
            </div>
          </div>

          <div className="relative animate-fade-in">
            <div className="absolute inset-0 -z-10 rounded-3xl bg-gradient-to-tr from-primary-200/40 via-primary-100/30 to-transparent blur-2xl" />
            <div className="card p-2 shadow-lg">
              <div className="rounded-xl bg-slate-900 text-slate-100 p-5 font-mono text-sm">
                <div className="flex gap-1.5 mb-3">
                  <span className="h-3 w-3 rounded-full bg-red-400" />
                  <span className="h-3 w-3 rounded-full bg-yellow-400" />
                  <span className="h-3 w-3 rounded-full bg-emerald-400" />
                </div>
                <pre className="whitespace-pre-wrap leading-relaxed">{`# AI Assistant: convert SQL to PySpark
sql = "select count(*) from employee where dept = 'DE'"

>>> df.filter(F.col("dept") == "DE")\\
       .agg(F.count("*").alias("cnt")) \\
       .show()
`}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="bg-white py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">
              Everything you need to run an exam
            </h2>
            <p className="mt-3 text-slate-600">
              Designed with HackerRank, LeetCode and Coursera in mind.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="card p-6 hover:shadow-md transition">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900">{f.title}</h3>
                <p className="mt-1 text-sm text-slate-600 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="courses" className="py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">
              Subjects we teach
            </h2>
            <p className="mt-3 text-slate-600">
              Full data engineering stack, taught free of cost as part of our NGO initiative.
            </p>
          </div>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            {COURSES.map((c) => (
              <span key={c} className="badge-primary px-3 py-1 text-sm">
                <GraduationCap className="h-3.5 w-3.5 mr-1.5" /> {c}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section id="faq" className="bg-white py-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6">
          <h2 className="text-3xl font-bold text-slate-900 text-center">FAQ</h2>
          <div className="mt-8 space-y-4">
            {[
              ['Is this free?', 'Yes - 100% free of cost as part of our NGO initiative.'],
              ['Do I need to install anything?', 'No, the platform runs entirely in your browser.'],
              ['Can I retake exams?', 'Only if your teacher enabled retakes for that exam.'],
              ['How are coding tests graded?', 'Hidden test cases run against your code automatically.'],
            ].map(([q, a]) => (
              <details key={q} className="card p-5 group">
                <summary className="flex items-center justify-between cursor-pointer text-slate-900 font-semibold">
                  {q}
                  <ArrowRight className="h-4 w-4 transition group-open:rotate-90" />
                </summary>
                <p className="mt-3 text-slate-600">{a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white py-8 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} Mewati Institute of Technology — Built with Django, DRF, React and Tailwind.
      </footer>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
    </div>
  );
}
