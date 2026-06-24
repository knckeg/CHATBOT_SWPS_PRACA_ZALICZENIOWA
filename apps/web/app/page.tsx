import React from 'react';
import Chat from './chat';

export default function HomePage() {
    return (
        <main className="container py-5">
            <div className="text-center mb-5">
                <h1 className="display-4 fw-bold text-dark">Projekt Zaliczeniowy SWPS</h1>
                <p className="lead text-muted">Interdyscyplinarny projekt łączący Psychologię i Informatykę</p>
                <hr className="my-4 mx-auto" style={{ maxWidth: '200px', borderTop: '3px solid #0d6efd' }} />
            </div>
            <Chat />
        </main>
    );
}
