export type Message = {
    role: 'user' | 'system' | 'assistant';
    content: string;
    color?: string;
    error?: boolean;
};
