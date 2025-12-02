import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { MessageCircle, X, Send } from "lucide-react";
import { useGenerateText } from "@/hooks/use-llm";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

const AIChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm Hopkins-Rotowire SmartChat 🏈 Ask me about player stats, team performance, injury reports, or any NFL-related questions.",
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const { mutate: generateText, isPending } = useGenerateText();

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isPending) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputValue,
      isBot: false,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue("");

    generateText(
      {
        prompt: currentInput,
        system_prompt: "You are an NFL analytics expert assistant. Provide helpful, accurate information about NFL players, teams, and statistics.",
        max_tokens: 500,
        temperature: 0.7
      },
      {
        onSuccess: (response) => {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now(),
              text: response.generated_text,
              isBot: true,
              timestamp: new Date()
            }
          ]);
        },
        onError: () => {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now(),
              text: "Sorry, I encountered an error. Please try again or check if the backend service is running.",
              isBot: true,
              timestamp: new Date()
            }
          ]);
        }
      }
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      {/* <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-primary to-accent hover:opacity-90 shadow-lg"
        size="icon"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-primary-foreground" />
        ) : (
          <MessageCircle className="w-6 h-6 text-primary-foreground" />
        )}
      </Button> */}

      {/* Chat Window */}
      {isOpen && (
        <Card className="fixed bottom-24 right-6 z-40 w-80 md:w-96 h-96 shadow-xl border-border">
          <CardHeader className="pb-3 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-t-lg">
            <CardTitle className="text-lg font-semibold">Hopkins-Rotowire SmartChat</CardTitle>
            <p className="text-sm text-primary-foreground/80">Ask me anything about the NFL 🏈</p>
          </CardHeader>
          
          <CardContent className="flex flex-col h-full p-0">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg text-sm ${
                      message.isBot
                        ? 'bg-muted text-foreground'
                        : 'bg-primary text-primary-foreground'
                    }`}
                  >
                    {message.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-border">
              <div className="flex space-x-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about the NFL..."
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isPending || !inputValue.trim()}
                  size="icon"
                  className="bg-accent hover:bg-accent/90"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
};

export default AIChatbot;