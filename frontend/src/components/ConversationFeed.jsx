import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import ContradictionCard from './ContradictionCard.jsx';

function AgentReply({ content, contradictionDetected, contradictedOpinion, timestamp, showTyping }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(!showTyping);

  useEffect(() => {
    if (!showTyping) {
      setDisplayed(content);
      setDone(true);
      return;
    }

    setDisplayed('');
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(content.slice(0, i));
      if (i >= content.length) {
        clearInterval(interval);
        setDone(true);
      }
    }, 15);

    return () => clearInterval(interval);
  }, [content, showTyping]);

  const borderClass = contradictionDetected
    ? 'border-l-accent-red'
    : 'border-l-border';

  return (
    <div>
      <div className={`border-l-2 ${borderClass} pl-4 py-1`}>
        <p className="text-sm text-primary leading-relaxed typing-cursor">
          {displayed}
          {!done && <span className="opacity-0">|</span>}
        </p>
        <div className="flex items-center gap-2 mt-1">
          {contradictionDetected && (
            <span className="text-[10px] font-semibold tracking-widest text-accent-red uppercase">
              Contradiction
            </span>
          )}
          <span className="text-[10px] text-secondary" title={timestamp}>
            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
          </span>
        </div>
      </div>
      {done && contradictionDetected && contradictedOpinion && (
        <div className="mt-3">
          <ContradictionCard contradictedOpinion={contradictedOpinion} />
        </div>
      )}
    </div>
  );
}

function UserMessage({ content, timestamp }) {
  return (
    <div className="flex justify-end">
      <div className="bg-surface border border-border rounded px-4 py-3 max-w-[80%]">
        <p className="text-sm text-primary leading-relaxed">{content}</p>
        <p className="text-[10px] text-secondary mt-1 text-right" title={timestamp}>
          {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
        </p>
      </div>
    </div>
  );
}

export default function ConversationFeed({ messages, showSlowIndicator }) {
  const bottomRef = useRef(null);
  const [hasAutoScrolled, setHasAutoScrolled] = useState(false);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (messages.length > 0 && !hasAutoScrolled) {
      setHasAutoScrolled(true);
    }
  }, [messages.length, hasAutoScrolled]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-md px-4"
        >
          <p className="text-secondary text-sm leading-relaxed">
            Tell me a World Cup take. I'll remember it.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
      <AnimatePresence initial={false}>
        {messages.map((msg, i) => (
          <motion.div
            key={`${msg.timestamp}-${i}`}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {msg.role === 'user' ? (
              <UserMessage content={msg.content} timestamp={msg.timestamp} />
            ) : (
              <AgentReply
                content={msg.content}
                contradictionDetected={msg.contradiction_detected}
                contradictedOpinion={msg.contradicted_opinion}
                timestamp={msg.timestamp}
                showTyping={i === messages.length - 1}
              />
            )}
          </motion.div>
        ))}
      </AnimatePresence>

      {showSlowIndicator && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 text-xs text-secondary pl-4"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent-indigo animate-pulse" />
          still thinking...
        </motion.div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
