import { useParams } from "react-router-dom";
import { Card } from "primereact/card";
import { ProgressSpinner } from "primereact/progressspinner";
import { useTranscription } from "../hooks/useTranscription";
import { TranscriptionSegmentItem } from "../components/transcription";

export function ResultsPage() {
  const { transcriptionId } = useParams<{ transcriptionId: string }>();
  const {
    data: transcription,
    isLoading,
    error,
  } = useTranscription(transcriptionId || "");

  if (isLoading) {
    return (
      <div
        style={{ display: "flex", justifyContent: "center", padding: "4rem" }}
      >
        <ProgressSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
        <Card>
          <h2>Error</h2>
          <p>Failed to load transcription</p>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Transcription Results</h1>
      <Card>
        <h3>{transcription?.fileName}</h3>
        <p>Duration: {transcription?.duration}s</p>
        <p>Status: {transcription?.status}</p>
        <div>
          <h4>Segments:</h4>
          {transcription?.segments.map((segment) => (
            <TranscriptionSegmentItem key={segment.id} segment={segment} />
          ))}
        </div>
      </Card>
    </div>
  );
}
