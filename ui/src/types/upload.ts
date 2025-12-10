export interface FileUploadRequest {
  file: File;
  options?: {
    language?: string;
    detectSpeakers?: boolean;
  };
}

export interface UrlUploadRequest {
  url: string;
  options?: {
    language?: string;
    detectSpeakers?: boolean;
  };
}

export interface UploadResponse {
  transcription_id: string;
  status: string;
  message: string;
}

export interface UploadProgress {
  percent: number;
  loaded: number;
  total: number;
}
