export type Status = "pending" | "processing" | "completed" | "failed";

export interface TranscriptionSegment {
  id: string;
  start_time: number;
  end_time: number;
  text: string;
  speaker?: string;
  confidence?: number;
}

export interface Transcription {
  id: string;
  status: Status;
  fileName: string;
  fileType: string;
  duration?: number;
  language?: string;
  segments: TranscriptionSegment[];
  createdAt: string;
  updatedAt: string;
  metadata?: {
    sourceUrl?: string;
    processingTime?: number;
  };
}

export interface TranscriptionUpdate {
  segments: TranscriptionSegment[];
}
