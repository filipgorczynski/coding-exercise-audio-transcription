import { Message } from "primereact/message";

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return <Message severity="error" text={message} />;
}
