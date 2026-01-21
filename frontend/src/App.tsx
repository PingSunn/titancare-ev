/**
 * Main application component
 */

import { useEffect } from "react";
import { ChatLayout, Sidebar, ChatArea } from "@/components/chat";
import { useChat, useSessions, useHealthCheck } from "@/hooks";

function App() {
  const {
    sessions,
    activeSessionId,
    activeSession,
    createSession,
    selectSession,
    deleteSession,
    updateSessionMessages,
  } = useSessions();

  const {
    isConnected,
    isChecking: isCheckingConnection,
    checkNow: checkConnection,
  } = useHealthCheck();

  const {
    messages,
    isLoading,
    sendMessage,
    setMessages,
  } = useChat({
    sessionId: activeSessionId ?? undefined,
    onSessionCreated: (sessionId) => {
      // Update session if it doesn't exist yet
      if (!sessions.find((s) => s.id === sessionId)) {
        createSession();
      }
    },
  });

  // Load messages when switching sessions
  useEffect(() => {
    if (activeSession) {
      setMessages(activeSession.messages);
    } else {
      setMessages([]);
    }
  }, [activeSessionId, activeSession, setMessages]);

  // Save messages to session when they change
  useEffect(() => {
    if (activeSessionId && messages.length > 0) {
      updateSessionMessages(activeSessionId, messages);
    }
  }, [messages, activeSessionId, updateSessionMessages]);

  // Handle new chat
  const handleNewChat = () => {
    createSession();
    setMessages([]);
  };

  // Handle send message
  const handleSendMessage = async (content: string) => {
    // Create session if none exists
    if (!activeSessionId) {
      createSession();
    }
    await sendMessage(content);
  };

  return (
    <ChatLayout
      sidebar={
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          isConnected={isConnected}
          isCheckingConnection={isCheckingConnection}
          onNewChat={handleNewChat}
          onSelectSession={selectSession}
          onDeleteSession={deleteSession}
          onCheckConnection={checkConnection}
        />
      }
    >
      <ChatArea
        messages={messages}
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
      />
    </ChatLayout>
  );
}

export default App;
