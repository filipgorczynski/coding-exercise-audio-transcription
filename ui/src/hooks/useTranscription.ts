import { useQuery } from "@tanstack/react-query";
import { transcriptionApi } from "../services/api/transcription";
import type { Transcription } from "../types/transcription";

export const useTranscription = (id: string) => {
  return useQuery({
    queryKey: ["transcription", id],
    queryFn: () => transcriptionApi.getTranscription(id),
    enabled: !!id,
  });
};

export const useListTranscriptions = () => {
  return useQuery({
    queryKey: ["transcriptions"],
    queryFn: () => transcriptionApi.listTranscriptions(),
    staleTime: 30000,
    refetchOnWindowFocus: true,
  });
};

export const useTranscriptionPolling = (id: string) => {
  return useQuery({
    queryKey: ["transcription", id],
    queryFn: () => transcriptionApi.getTranscription(id),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data as Transcription | undefined;
      if (data?.status === "processing") {
        return 3000;
      }
      return false;
    },
    refetchIntervalInBackground: false,
    staleTime: 0,
  });
};
