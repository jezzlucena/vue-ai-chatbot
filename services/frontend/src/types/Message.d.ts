export type Message = {
    role: 'user' | 'system' | 'assistant';
    content: string;
    error?: boolean;
};