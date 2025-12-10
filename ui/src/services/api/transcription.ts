import { apiClient } from "./client";
import axios from "axios";
import type {
  Transcription,
  TranscriptionUpdate,
} from "../../types/transcription";
import type { UploadResponse } from "../../types/upload";

export const transcriptionApi = {
  uploadFile: async (
    file: File,
    options?: { language?: string; detectSpeakers?: boolean },
    onProgress?: (progress: number) => void,
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    if (options?.language) formData.append("language", options.language);
    if (options?.detectSpeakers) formData.append("detect_speakers", "true");

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
    options?: { language?: string; detectSpeakers?: boolean },
  ): Promise<UploadResponse> => {
    return apiClient.post("/api/transcriptions/upload-url", {
      url,
      language: options?.language || "en",
      detect_speakers: options?.detectSpeakers || false,
    });
  },

  getTranscription: async (id: string): Promise<Transcription> => {
    return apiClient.get(`/api/transcriptions/${id}`);
  },

  updateTranscription: async (
    id: string,
    update: TranscriptionUpdate,
  ): Promise<Transcription> => {
    return apiClient.patch(`/api/transcriptions/${id}`, update);
  },

  deleteTranscription: async (id: string): Promise<void> => {
    return apiClient.delete(`/api/transcriptions/${id}`);
  },

  exportTranscription: async (
    id: string,
    format: "txt" | "docx" | "srt",
  ): Promise<Blob> => {
    const response = await axios.get(
      `${apiClient.defaults.baseURL}/api/transcriptions/${id}/export`,
      {
        params: { format },
        responseType: "blob",
      },
    );
    return response.data;
  },
};
