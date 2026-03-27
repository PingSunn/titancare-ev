import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Maximize2, Minimize2 } from 'lucide-react';

const ChatWidget = () => {
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    
    // 1. สร้าง State สำหรับระบบแชท
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'สวัสดีครับ มีข้อมูลรถหรือบริการอะไรให้เราช่วยดูแลไหมครับ?' }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // สร้าง Session ID แบบสุ่มเพื่อให้ AI จำบริบทการคุยได้
    const [sessionId] = useState(() => crypto.randomUUID());
    
    // Ref สำหรับเลื่อนหน้าจอลงมาล่างสุดเวลามีข้อความใหม่
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    // 2. ฟังก์ชันส่งข้อความไปหา Backend
    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userText = inputValue;
        
        // เพิ่มข้อความผู้ใช้ลงในหน้าจอทันที
        setMessages(prev => [...prev, { sender: 'user', text: userText }]);
        setInputValue('');
        setIsLoading(true);

        try {
            // ยิง API ไปที่ LangGraph Backend ของคุณ
            const response = await fetch('http://localhost:8000/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: userText
                })
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            
            // นำคำตอบจาก AI มาแสดง
            setMessages(prev => [...prev, { sender: 'bot', text: data.reply }]);

        } catch (error) {
            console.error("Chat API Error:", error);
            setMessages(prev => [...prev, { 
                sender: 'bot', 
                text: 'ขออภัยครับ เซิร์ฟเวอร์ไม่สามารถตอบสนองได้ในขณะนี้ กรุณาลองใหม่อีกครั้งครับ' 
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    // รองรับการกด Enter เพื่อส่งข้อความ
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    const chatPanelStyle = isExpanded ? {
        position: 'fixed', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '620px', height: '720px',
        backgroundColor: 'white',
        borderRadius: '16px', boxShadow: '0 20px 60px rgba(0,0,0,0.35)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden', border: '1px solid #e5e7eb',
        zIndex: 10000,
        animation: 'chatSlideIn 0.3s ease-out'
    } : {
        width: '350px', height: '500px',
        backgroundColor: 'white',
        borderRadius: '16px', boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
        display: 'flex', flexDirection: 'column', marginBottom: '20px',
        overflow: 'hidden', border: '1px solid #e5e7eb',
        animation: 'chatSlideIn 0.3s ease-out'
    };

    return (
        <div style={{
            position: 'fixed', bottom: '30px', right: '30px',
            zIndex: 9999, display: 'flex', flexDirection: 'column', alignItems: 'flex-end'
        }}>

            {isChatOpen && isExpanded && (
                <div style={{
                    position: 'fixed', inset: 0,
                    backgroundColor: 'rgba(0,0,0,0.4)',
                    zIndex: 9999,
                    animation: 'fadeIn 0.2s ease-out'
                }} onClick={() => setIsExpanded(false)} />
            )}

            {isChatOpen && (
                <div style={chatPanelStyle}>
                    <div style={{ padding: '16px', backgroundColor: '#007bff', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 'bold' }}>Titan Care Assistant</span>
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', opacity: 0.85 }}
                            title={isExpanded ? 'Collapse' : 'Expand'}
                        >
                            {isExpanded ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
                        </button>
                    </div>
                    
                    {/* พื้นที่แสดงข้อความ */}
                    <div style={{ flex: 1, padding: '16px', backgroundColor: '#f9fafb', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        
                        {messages.map((msg, index) => (
                            <div key={index} style={{
                                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                                backgroundColor: msg.sender === 'user' ? '#e5e7eb' : '#007AFF',
                                color: msg.sender === 'user' ? '#111827' : '#ffffff',
                                padding: '12px',
                                borderRadius: '12px',
                                borderBottomRightRadius: msg.sender === 'user' ? '2px' : '12px',
                                borderBottomLeftRadius: msg.sender === 'bot' ? '2px' : '12px',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                                fontSize: '14px',
                                maxWidth: '85%',
                                lineHeight: '1.5',
                                whiteSpace: 'pre-wrap' // รองรับการขึ้นบรรทัดใหม่จาก AI
                            }}>
                                {msg.text}
                            </div>
                        ))}

                        {/* สถานะกำลังพิมพ์ */}
                        {isLoading && (
                            <div style={{
                                alignSelf: 'flex-start', backgroundColor: '#007AFF', color: 'white',
                                padding: '8px 12px', borderRadius: '12px', borderBottomLeftRadius: '2px',
                                fontSize: '12px', opacity: 0.7
                            }}>
                                กำลังพิมพ์...
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* พื้นที่พิมพ์ข้อความ */}
                    <div style={{ padding: '12px', borderTop: '1px solid #eee', display: 'flex', gap: '8px', alignItems: 'center', backgroundColor: 'white' }}>
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={isLoading}
                            placeholder="พิมพ์ข้อความ..."
                            style={{ flex: 1, padding: '10px 16px', borderRadius: '20px', border: '1px solid #ddd', outline: 'none', fontSize: '14px' }}
                        />
                        <button 
                            onClick={handleSendMessage}
                            disabled={isLoading || !inputValue.trim()}
                            style={{ 
                                color: inputValue.trim() && !isLoading ? '#007bff' : '#9ca3af',
                                background: 'none', border: 'none', cursor: inputValue.trim() && !isLoading ? 'pointer' : 'default',
                                padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            )}

            <button
                onClick={() => setIsChatOpen(!isChatOpen)}
                style={{
                    width: '60px', height: '60px', borderRadius: '50%',
                    backgroundColor: isChatOpen ? '#333' : '#007bff',
                    color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
                    transition: 'all 0.3s ease', border: 'none'
                }}
            >
                {isChatOpen ? <X size={28} /> : <MessageCircle size={28} />}
            </button>

            <style>{`
                @keyframes chatSlideIn {
                  from { opacity: 0; transform: translateY(20px) scale(0.95); }
                  to { opacity: 1; transform: translateY(0) scale(1); }
                }
                @keyframes fadeIn {
                  from { opacity: 0; }
                  to { opacity: 1; }
                }
            `}</style>
        </div>
    );
};

export default ChatWidget;