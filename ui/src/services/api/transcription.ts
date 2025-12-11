import { apiClient } from "./client";
import type {
  Transcription,
  TranscriptionItem,
} from "../../types/transcription";

export const transcriptionApi = {
  uploadFile: async (
    file: File,
    // options?: { language?: string; detectSpeakers?: boolean },
    onProgress?: (progress: number) => void,
  ): Promise<Transcription> => {
    const formData = new FormData();
    formData.append("file", file);
    // if (options?.language) formData.append("language", options.language);
    // if (options?.detectSpeakers) formData.append("detect_speakers", "true");

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

  uploadFromUrl: async (
    url: string,
    // options?: { language?: string; detectSpeakers?: boolean },
  ): Promise<Transcription> => {
    return apiClient.post("/api/transcriptions/upload-url", {
      url,
      // language: options?.language || "en",
      // detect_speakers: options?.detectSpeakers || false,
    });
  },

  listTranscriptions: async (): Promise<TranscriptionItem[]> => {
    return apiClient.get("/api/transcriptions");
  },

  getTranscription: async (id: string): Promise<Transcription> => {
    return apiClient.get(`/api/transcriptions/${id}`);
  },
};
