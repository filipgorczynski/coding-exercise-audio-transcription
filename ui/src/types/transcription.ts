export type Status = "pending" | "processing" | "completed" | "failed";

export interface TranscriptionItem {
  id: string;
  status: Status;
  file_name: string;
  duration?: number;
}

export interface TranscriptionSegment {
  id: string;
  start_time: number;
  end_time: number;
  text: string;
  speaker?: string;
}

export interface Transcription {
  id: string;
  status: Status;
  fileName: string;
  fileType: string;
  duration?: number;
  language?: string;
  segments: TranscriptionSegment[];
}

export interface TranscriptionUpdate {
  segments: TranscriptionSegment[];
}
