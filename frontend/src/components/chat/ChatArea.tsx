/**
 * Chat area with messages and input
 */

import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import type { Message } from "@/types";

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
}

export function ChatArea({ messages, isLoading, onSendMessage }: ChatAreaProps) {
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
}
