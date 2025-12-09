import { apiClient } from "./client";
import type {
  Transcription,
  TranscriptionItem,
} from "../../types/transcription";

export const transcriptionApi = {
  uploadFile: async (
    file: File,
    onProgress?: (progress: number) => void,
  ): Promise<Transcription> => {
    const formData = new FormData();
    formData.append("file", file);

    // TODO(fgorczynski): export to URL constants
    return apiClient.post("/api/transcriptions/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = (progressEvent.loaded * 100) / progressEvent.total;
          onProgress(percent);
        }
      },
    });
  },

  uploadFromUrl: async (url: string): Promise<Transcription> => {
    return apiClient.post("/api/transcriptions/upload-url", {
      url,
    });
  },

  listTranscriptions: async (): Promise<TranscriptionItem[]> => {
    return apiClient.get("/api/transcriptions");
  },

  getTranscription: async (id: string): Promise<Transcription> => {
    return apiClient.get(`/api/transcriptions/${id}`);
  },
};
