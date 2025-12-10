import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transcriptionApi } from "../services/api/transcription";
import type { TranscriptionUpdate } from "../types/transcription";

export const useTranscription = (id: string) => {
  return useQuery({
    queryKey: ["transcription", id],
    queryFn: () => transcriptionApi.getTranscription(id),
    enabled: !!id,
  });
};

export const useUpdateTranscription = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (update: TranscriptionUpdate) =>
      transcriptionApi.updateTranscription(id, update),
    onSuccess: (data) => {
      queryClient.setQueryData(["transcription", id], data);
    },
  });
};

export const useExportTranscription = () => {
  return useMutation({
    mutationFn: ({
      id,
      format,
    }: {
      id: string;
      format: "txt" | "docx" | "srt";
    }) => transcriptionApi.exportTranscription(id, format),
    onSuccess: (blob, variables) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `transcription.${variables.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });
};
