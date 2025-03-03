/**
 * Type that represents a chat message, with the role of
 * the sender, color (in case it is a user message),
 * content (optional, as typing indicators are empty messages),
 * and error flag.
 */
export type Message = {
  role: 'user' | 'system' | 'assistant'
  content?: string
  color?: string
  error?: boolean
}
