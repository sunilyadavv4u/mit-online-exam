import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { Bot, Loader2, MessageCircle, Send, Trash2, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { mitChatApi } from '../../api/endpoints';
import { formatApiError } from '../../utils/helpers';

const ROLE_HINTS = {
  student: 'Ask about Python, SQL, PySpark, Azure, DSA, Java — study help, not exam answers.',
  teacher: 'Plan lessons, draft question ideas, or explain topics for your class.',
  super_admin: 'Platform guidance, exam workflows, and technical questions.',
};

const STARTERS = {
  student: [
    'Explain PySpark DataFrame vs pandas in simple terms',
    'What is the difference between SQL JOIN types?',
    'How do I debug a Python IndexError?',
  ],
  teacher: [
    'Suggest 5 MCQ questions on Python lists for beginners',
    'Outline a 60-minute lesson on Azure Data Factory',
    'How should I explain Spark transformations to students?',
  ],
  super_admin: [
    'Summarize best practices for online exam proctoring',
    'How do teacher and student roles differ on this platform?',
    'Tips for scaling a Django exam application',
  ],
};

function Bubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-primary-600 text-white' : 'bg-slate-200 text-slate-700'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? 'bg-primary-600 text-white rounded-tr-sm'
            : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm shadow-sm'
        }`}
      >
        {msg.content}
      </div>
    </div>
  );
}

export default function MITChatPage() {
  const { user } = useAuth();
  const role = user?.role || 'student';
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;

    const userMsg = { role: 'user', content };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);

    try {
      const r = await mitChatApi.send(nextMessages);
      const reply = r.data?.message;
      if (reply?.content) {
        setMessages((prev) => [...prev, { role: 'assistant', content: reply.content }]);
      }
    } catch (err) {
      toast.error(formatApiError(err, 'AI chat failed — check Databricks settings'));
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setInput('');
  };

  const starters = STARTERS[role] || STARTERS.student;

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between gap-3 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-primary-600 text-white flex items-center justify-center">
            <MessageCircle className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">MIT AI Chat</h1>
            <p className="text-xs text-slate-500">
              Powered by Databricks Llama-4 Maverick ·{' '}
              <span className="capitalize">{role.replace('_', ' ')}</span> mode
            </p>
          </div>
        </div>
        {messages.length > 0 && (
          <button type="button" onClick={clearChat} className="btn-secondary py-1.5 text-sm">
            <Trash2 className="h-4 w-4" /> New chat
          </button>
        )}
      </div>

      <p className="text-sm text-slate-600 py-2">{ROLE_HINTS[role] || ROLE_HINTS.student}</p>

      <div className="flex-1 overflow-y-auto space-y-4 py-4 px-1 min-h-0">
        {messages.length === 0 && !loading && (
          <div className="space-y-4">
            <p className="text-center text-slate-500 text-sm">Start a conversation</p>
            <div className="flex flex-wrap justify-center gap-2">
              {starters.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => send(s)}
                  className="text-left text-sm px-3 py-2 rounded-xl border border-slate-200 bg-white hover:border-primary-300 hover:bg-primary-50 text-slate-700 max-w-xs"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <Bubble key={`${i}-${m.role}`} msg={m} />
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200">
              <Bot className="h-4 w-4 text-slate-600" />
            </div>
            <div className="rounded-2xl rounded-tl-sm bg-white border border-slate-200 px-4 py-3 shadow-sm">
              <Loader2 className="h-5 w-5 animate-spin text-primary-600" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-slate-200 pt-4 pb-2">
        <div className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            rows={2}
            className="input flex-1 resize-none min-h-[48px] max-h-32"
            placeholder="Message MIT AI Chat… (Enter to send, Shift+Enter for new line)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="btn-primary h-12 px-4 shrink-0"
            aria-label="Send message"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
