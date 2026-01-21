# TitanCare Frontend

React chat interface built with Vite, TypeScript, Tailwind CSS v4, and shadcn/ui.

## Tech Stack

- **React 19** - UI framework
- **Vite 7** - Build tool
- **TypeScript 5** - Type safety
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - UI components (Radix UI)
- **lucide-react** - Icons
- **react-markdown** - Markdown rendering

## Project Structure

```
src/
├── components/
│   ├── chat/               # Chat UI components
│   │   ├── ChatLayout.tsx      # Main layout (sidebar + chat)
│   │   ├── Sidebar.tsx         # Session list
│   │   ├── ChatArea.tsx        # Messages + input
│   │   ├── MessageList.tsx     # Message display
│   │   ├── MessageBubble.tsx   # Single message
│   │   └── ChatInput.tsx       # Input field
│   └── ui/                 # shadcn components
├── hooks/
│   ├── useChat.ts          # Chat state management
│   └── useSessions.ts      # Session persistence
├── services/
│   └── api.ts              # Backend API client
├── types/
│   └── index.ts            # TypeScript interfaces
├── lib/
│   └── utils.ts            # Utility functions (cn)
├── App.tsx                 # Main app
├── main.tsx                # Entry point
└── index.css               # Tailwind + theme
```

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Type check
npx tsc --noEmit

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env.local` file (optional):

```env
VITE_API_URL=http://localhost:8000/api
```

## Adding shadcn Components

```bash
npx shadcn@latest add [component-name]
```

Available at: https://ui.shadcn.com/docs/components
