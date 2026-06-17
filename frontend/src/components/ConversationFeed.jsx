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

  return (
    <div>
      <div className="glass rounded-xl px-5 py-4 max-w-[85%]">
        <p className="text-sm text-primary leading-relaxed typing-cursor">
          {displayed}
          {!done && <span className="opacity-0">|</span>}
        </p>
        <div className="flex items-center gap-2 mt-2">
          {contradictionDetected && (
            <span className="text-[10px] font-semibold tracking-widest text-accent-red">
              Contradiction
            </span>
          )}
          <span className="text-[10px] text-secondary" title={timestamp}>
            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
          </span>
        </div>
      </div>
      {done && contradictionDetected && contradictedOpinion && (
        <div className="mt-3 pl-2">
          <ContradictionCard contradictedOpinion={contradictedOpinion} />
        </div>
      )}
    </div>
  );
}

function UserMessage({ content, timestamp }) {
  return (
    <div className="flex justify-end">
      <div className="glass rounded-xl px-5 py-4 max-w-[85%]">
        <p className="text-sm text-primary leading-relaxed">{content}</p>
        <p className="text-[10px] text-secondary mt-2 text-right" title={timestamp}>
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
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="text-center max-w-md px-4"
        >
          <div className="text-4xl mb-4 opacity-30">💬</div>
          <p className="text-secondary text-sm leading-relaxed">
            Tell me a World Cup take. I'll remember it and call you out if you flip-flop.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6 space-y-4">
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
          className="flex items-center gap-2 text-xs text-secondary pl-5"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent-indigo animate-pulse" />
          still thinking...
        </motion.div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
