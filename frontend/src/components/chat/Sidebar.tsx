/**
 * Sidebar with session list and new chat button
 */

import { Plus, MessageSquare, Trash2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import type { Session } from "@/types";
import { cn } from "@/lib/utils";

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  isConnected: boolean;
  isCheckingConnection: boolean;
  onNewChat: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onCheckConnection: () => void;
}

export function Sidebar({
  sessions,
  activeSessionId,
  isConnected,
  isCheckingConnection,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onCheckConnection,
}: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="p-4">
        <h1 className="text-lg font-semibold text-sidebar-foreground">
          TitanCare
        </h1>
      </div>

      <div className="px-3">
        <Button
          onClick={onNewChat}
          className="w-full justify-start gap-2"
          variant="outline"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Separator className="my-4" />

      {/* Session list */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1">
          {sessions.length === 0 ? (
            <p className="px-2 py-4 text-sm text-muted-foreground">
              No conversations yet
            </p>
          ) : (
            sessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={session.id === activeSessionId}
                onSelect={() => onSelectSession(session.id)}
                onDelete={() => onDeleteSession(session.id)}
              />
            ))
          )}
        </div>
      </ScrollArea>

      {/* Connection Status */}
      <Separator className="my-2" />
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "h-2.5 w-2.5 rounded-full",
                isCheckingConnection && "animate-pulse bg-yellow-500",
                !isCheckingConnection && isConnected && "bg-green-500",
                !isCheckingConnection && !isConnected && "bg-red-500"
              )}
            />
            <span className="text-xs text-muted-foreground">
              {isCheckingConnection
                ? "Checking..."
                : isConnected
                ? "Connected"
                : "Disconnected"}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={onCheckConnection}
            disabled={isCheckingConnection}
          >
            <RefreshCw
              className={cn(
                "h-3 w-3 text-muted-foreground",
                isCheckingConnection && "animate-spin"
              )}
            />
          </Button>
        </div>
      </div>
    </div>
  );
}

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
}: SessionItemProps) {
  return (
    <div
      className={cn(
        "group flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors",
        "hover:bg-sidebar-accent cursor-pointer",
        isActive && "bg-sidebar-accent"
      )}
      onClick={onSelect}
    >
      <MessageSquare className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
      <span className="flex-1 truncate text-sidebar-foreground">
        {session.title}
      </span>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 opacity-0 group-hover:opacity-100"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <Trash2 className="h-3 w-3 text-muted-foreground hover:text-destructive" />
      </Button>
    </div>
  );
}
