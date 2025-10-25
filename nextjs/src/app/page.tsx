import { Suspense } from "react";
import { ChatProvider } from "@/components/chat/ChatProvider";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { AuthGuard } from "@/components/AuthGuard";

export default function HomePage(): React.JSX.Element {
  return (
    <AuthGuard>
      <div className="flex flex-col h-screen">
        <Suspense fallback={<div>Loading AI Stock Analysis...</div>}>
          <ChatProvider>
            <ChatContainer />
          </ChatProvider>
        </Suspense>
      </div>
    </AuthGuard>
  );
}
