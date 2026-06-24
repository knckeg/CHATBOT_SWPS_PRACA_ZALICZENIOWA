'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5001/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    history: messages,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
            } else {
                setMessages((prev) => [...prev, { role: 'assistant', content: `Coś poszło nie tak: ${data.error}` }]);
            }
        } catch (error) {
            setMessages((prev) => [...prev, { role: 'assistant', content: 'Błąd połączenia z serwerem API.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card shadow-sm col-md-8 mx-auto">
            <div className="card-header bg-primary text-white d-flex align-items-center justify-content-between">
                <h5 className="mb-0">🤖 Asystent Naukowy RAG - SWPS</h5>
                <span className="badge bg-light text-primary">Status: Aktywny</span>
            </div>

            <div className="card-body p-4" style={{ height: '450px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
                {messages.length === 0 && (
                    <div className="text-center text-muted my-5">
                        <p className="fs-5">Cześć! Jestem Twoim inteligentnym asystentem Uniwersytetu SWPS.</p>
                        <small>Zadaj mi dowolne pytanie ogólne lub poproś o znalezienie publikacji naukowej z dziedziny psychologii!</small>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={index} className={`d-flex mb-3 ${msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}>
                        <div
                            className={`p-3 rounded-3 shadow-sm ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-white text-dark border'}`}
                            style={{ maxWidth: '75%', whiteSpace: 'pre-wrap' }}
                        >
                            <strong>{msg.role === 'user' ? 'Ty' : 'Bot'}:</strong>
                            <div className="mt-1">{msg.content}</div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="d-flex justify-content-start mb-3">
                        <div className="p-3 bg-white border text-muted rounded-3 shadow-sm d-flex align-items-center">
                            <div className="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                            <span>Przeszukuję bazę danych i generuję odpowiedź...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="card-footer bg-white border-top-0 p-3">
                <form onSubmit={handleSubmit} className="input-group">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Napisz pytanie (np. 'Znajdź publikacje o psychologii klinicznej')..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                    />
                    <button className="btn btn-primary px-4" type="submit" disabled={isLoading}>
                        Wyślij
                    </button>
                </form>
            </div>
        </div>
    );
}
}
