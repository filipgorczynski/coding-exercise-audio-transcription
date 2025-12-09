import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { transcriptionApi } from "../services/api/transcription";

export const useFileUpload = () => {
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: (params: { file: File; options?: any }) =>
      transcriptionApi.uploadFile(params.file, params.options, setProgress),
    onSuccess: (data) => {
      navigate(`/results/${data.id}`);
    },
  });

  return { ...mutation, progress };
};

export const useUrlUpload = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (params: { url: string; options?: any }) =>
      transcriptionApi.uploadFromUrl(params.url, params.options),
    onSuccess: (data) => {
      navigate(`/results/${data.id}`);
    },
  });
};
