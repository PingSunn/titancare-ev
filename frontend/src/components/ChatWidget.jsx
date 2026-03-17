import React, { useState } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

const ChatWidget = () => {
    const [isChatOpen, setIsChatOpen] = useState(false);

    return (
        <div style={{
            position: 'fixed',
            bottom: '30px',
            right: '30px',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end'
        }}>

            {isChatOpen && (
                <div style={{
                    width: '350px',
                    height: '500px',
                    backgroundColor: 'white',
                    borderRadius: '16px',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
                    display: 'flex',
                    flexDirection: 'column',
                    marginBottom: '20px',
                    overflow: 'hidden',
                    border: '1px solid #e5e7eb',
                    animation: 'chatSlideIn 0.3s ease-out'
                }}>
                    <div style={{ padding: '16px', backgroundColor: '#007bff', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 'bold' }}>Titan Care Chat</span>
                    </div>
                    <div style={{ flex: 1, padding: '16px', backgroundColor: '#f9fafb', overflowY: 'auto' }}>

                        <div style={{
                            backgroundColor: '#007AFF', 
                            color: '#ffffff',           
                            padding: '12px',
                            borderRadius: '12px',
                            borderBottomLeftRadius: '2px',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            fontSize: '14px',
                            maxWidth: '85%',
                            lineHeight: '1.5'         
                        }}>
                            สวัสดีครับ มีอะไรให้เราช่วยดูแลไหมครับ?
                        </div>

                    </div>

                    <div style={{ padding: '12px', borderTop: '1px solid #eee', display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <input
                            type="text"
                            placeholder="พิมพ์ข้อความ..."
                            style={{ flex: 1, padding: '8px 16px', borderRadius: '20px', border: '1px solid #ddd', outline: 'none', fontSize: '14px' }}
                        />
                        <button style={{ color: '#007bff' }}><Send size={20} /></button>
                    </div>
                </div>
            )}

            <button
                onClick={() => setIsChatOpen(!isChatOpen)}
                style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    backgroundColor: isChatOpen ? '#333' : '#007bff',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
                    transition: 'all 0.3s ease',
                    border: 'none'
                }}
            >
                {isChatOpen ? <X size={28} /> : <MessageCircle size={28} />}
            </button>

            <style>{`
        @keyframes chatSlideIn {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
        </div>
    );
};

export default ChatWidget;